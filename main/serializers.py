from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'fullname', 'first_name', 'last_name', 'email']

    fullname = serializers.CharField(source='get_full_name')
