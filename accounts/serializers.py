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

    def create(self, validated_data):
        name = validated_data.pop("name", "")
        email = validated_data["email"].lower()
        first, _, last = name.partition(" ")
        user = User(username=email, email=email, first_name=first, last_name=last)
        user.set_password(validated_data["password"])
        user.save()
        return user
