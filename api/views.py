from django.shortcuts import render

from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound

from api.serializers import UserSerializer, SurveySerializer

import simplejson as json
import base64

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from polls.models import Survey, SurveySection, Survey_Question, Choice

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))		
@csrf_exempt
def getSurveyDetail(request, pk, format=None):
	response_dict = {}
	survey = Survey.objects.get(pk=pk)
	response_dict['id'] = pk
	response_dict['survey_name'] = survey.survey_name
	response_dict['user'] = survey.user.id
	response_dict['pub_date'] = survey.pub_date
	response_dict['expiry_date'] = survey.expiry
	response_dict['description'] = survey.description
	response_dict['number_sections'] = survey.number_sections
	response_dict['survey_sections'] = []


	surveySection = SurveySection.objects.filter(survey=survey).order_by('sectionOrder')

	for section in surveySection:
		tempSection = {}
		tempSection['name'] = section.sectionName
		tempSection['questions'] = []
		surveyQuestions = Survey_Question.objects.filter(survey=survey).filter(section=section)
		for question in surveyQuestions:
			tempQuestion = {}
			tempQuestion['id'] = question.question.id
			tempQuestion['text'] = question.question.question_text
			tempQuestion['type'] = question.question_type
			tempQuestion['description'] = question.question.description
			tempQuestion['addComment'] = question.add_comment
			tempQuestion['mandatory'] = question.mandatory

			if question.question_type == 'radio' or question.question_type == 'checkbox':
				choices = []
				questionChoices = Choice.objects.filter(question=question.question)
				for choice in questionChoices:
					tempChoice = {}
					tempChoice['text'] = choice.choice_text
					if choice.choice_image:
						tempChoice['image'] = str(choice.choice_image)
					else:
						tempChoice['image'] = None
					choices.append(tempChoice)
			tempQuestion['choices'] = choices
		tempSection['questions'].append(tempQuestion) 
		response_dict['survey_sections'].append(tempSection)
	return JSONResponse(response_dict)

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))		
@csrf_exempt
def getSurveyList(request, user, format=None):
	if request.method == 'GET':
		response_dict = {}
		surveyList = Survey.objects.filter(user=user)
		if surveyList:
			response_dict["user"] = user
			response_dict["survey"] = []
			for survey in surveyList:
				temp = {}
				temp["id"] = survey.id
				temp["name"] = survey.survey_name
				temp["description"] = survey.description
				temp["pub_date"] = survey.pub_date
				temp["expiry"] = survey.expiry
				temp["number_sections"] = survey.number_sections
				temp["expected_time"] = survey.expected_time
				response_dict["survey"].append(temp)
		else:
			response_dict["error"] = "No Survey Created by user"
			return JSONResponse(json.dumps(response_dict), status=400)
		return JSONResponse(response_dict)

class AuthToken(ObtainAuthToken):
	def post(self, request, *args, **kwargs):
		encodedcredentials = request.data.get('credentials')
		decodedcredentials = base64.b64decode(encodedcredentials).decode('ascii')
		username, password = decodedcredentials.split(':')
		tempdict = {'username':username, 'password':password}
		serializer = self.serializer_class(data=tempdict)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		token, created = Token.objects.get_or_create(user=user)
		extendeduser = {}
		if user.extendeduser.imageUrl:
			extendeduser['imageUrl'] = str(user.extendeduser.imageUrl)
		else:
			extendeduser['imageUrl'] = str(user.extendeduser.imageUrl)
		extendeduser['birthDay'] = user.extendeduser.birthDay
		extendeduser['gender'] = user.extendeduser.gender
		extendeduser['city'] = user.extendeduser.city
		extendeduser['state'] = user.extendeduser.state
		extendeduser['country'] = user.extendeduser.country
		extendeduser['bio'] = user.extendeduser.bio
		extendeduser['profession'] = user.extendeduser.profession
		extendeduser['user_slug'] = user.extendeduser.user_slug
		extendeduser['categories'] = user.extendeduser.categories
		extendeduser['credits'] = user.extendeduser.credits
		extendeduser['company_id'] = user.extendeduser.company_id
		return Response({'token': token.key, 'id':user.id, 'username':user.username, 'email': user.email, 'firstname':user.first_name, 'lastname':user.last_name, 'extendeduser':extendeduser})