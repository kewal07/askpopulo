from django.contrib.auth.models import User, Group
from polls.models import Survey
from rest_framework import serializers
from login.models import ExtendedUser


class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ('id','imageUrl', 'city', 'state', 'country')


class UserSerializer(serializers.ModelSerializer):
    extendeduser = ExtendedUserSerializer()
    class Meta:
        model = User
        fields = ('id','username', 'email', 'first_name', 'last_name', 'extendeduser')
        
    def create(self, validated_data):
        print(validated_data)
        extendeduser_data = validated_data.pop('extendeduser')
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user