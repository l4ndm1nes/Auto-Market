from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, EmailVerification
from .tasks import send_verification_email_task


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'phone_number')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        self.send_verification_email(user)

        return user

    def send_verification_email(self, user):
        from .models import EmailVerification
        from django.utils import timezone
        import uuid

        verification = EmailVerification.objects.create(
            user=user,
            code=uuid.uuid4(),
            expiration=timezone.now() + timezone.timedelta(hours=48)
        )

        send_verification_email_task.delay(user.id, verification.code, user.email)


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.UUIDField()

    def validate_code(self, value):
        try:
            verification = EmailVerification.objects.get(code=value)
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code.")

        if verification.is_expired():
            raise serializers.ValidationError("Verification code has expired.")

        return value

    def save(self, **kwargs):
        verification = EmailVerification.objects.get(code=self.validated_data['code'])
        user = verification.user
        user.is_verified = True
        user.is_active = True
        user.save()
        verification.delete()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError('Your account is not verified.')

        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_verified']
        read_only_fields = ['email', 'is_verified']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance

class ProfileDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("You must confirm the deletion.")
        return value