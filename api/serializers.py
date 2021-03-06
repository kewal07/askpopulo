from django.contrib.auth.models import User, Group
from polls.models import Survey, Survey_Question, Question, SurveySection
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

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question()
        fields = ('question_text', 'pub_date', 'expiry', 'description', 'que_slug')

class SurveySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySection()
        fields = ('sectionName', 'sectionOrder')

class SurveyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    section = SurveySectionSerializer()
    class Meta:
        model = Survey_Question
        fields = ('id', 'question', 'question_type', 'add_comment', 'mandatory', 'max_value', 'min_value', 'section')

class SurveySerializer(serializers.ModelSerializer):
    #survey_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    survey_question = SurveyQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Survey
        fields = ('id', 'survey_name', 'user', 'pub_date', 'expiry', 'description', 'number_sections', 'survey_question')