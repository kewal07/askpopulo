from django.shortcuts import render

from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound

from api.serializers import UserSerializer, SurveySerializer

import simplejson as json

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from polls.models import Survey

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Survey.objects.all()
	serializer_class = SurveySerializer


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