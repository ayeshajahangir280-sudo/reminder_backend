from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "email", "first_name", "last_name")

    def get_name(self, obj):
        return obj.get_full_name() or obj.email


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "email", "name", "password")

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def create(self, validated_data):
        name = validated_data.pop("name", "")
        email = validated_data["email"]
        first, _, last = name.partition(" ")
        user = User(username=email, email=email, first_name=first, last_name=last)
        user.set_password(validated_data["password"])
        user.save()
        return user
