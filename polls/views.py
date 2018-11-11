# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core import serializers

import json
import ConferenceType

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData
from be.models.CsvDataBuilder import CsvDataBuilder
from be.models.CsvData import CsvData
from users.models import Session, SessionManager
from users import *
# Create your views here.
# Note: a view is a func taking the HTTP request and returns sth accordingly

def index(request):
	return HttpResponse("Hello, world. You're at the polls index. =)")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request! =)</h1>")

# Note: csr: cross site request, adding this to enable request from localhost
@csrf_exempt
def uploadData(request):
	print ("Inside the upload function!!")
	if request.method == 'POST':

		dataDictionary = {}
		dataDictionary = (request.POST).dict()
		requestType = dataDictionary.get("request")
		print dataDictionary
		print requestType

		if request.FILES and "uploadSession" == requestType:
			data = uploadCSVFiles(request)
		elif "getSession" == requestType:
			data = {'result': getSession(dataDictionary)}
		elif "deleteSession" == requestType:
			data = {'result': deleteSession(dataDictionary)}
		elif "saveSession" == requestType:
			data = {'result': saveSession(dataDictionary)}
		elif "getAll" == requestType:
			data = getSessionsByEmail(dataDictionary)
		elif "register" == requestType:
			userCreated = registerUser(dataDictionary)
			data = userCreated
		elif "login" == requestType:
			data = loginUser(dataDictionary)
		else:
			print ("ERROR: file should have been rejected by frontend already")

		if request.POST:
			# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print ("Now we got the csv file =)")

		return HttpResponse(json.dumps(data))
		# return HttpResponse("Got the CSV file.")
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')


def uploadCSVFiles(request):
	hasFiles = [False] * 3 

	csvFiles = {}
	csvFileList = request.FILES.getlist('file')

	csvDataBuilder = CsvDataBuilder()

	for csvFile in csvFileList:
		print (len(csvFile))
		
		fileName = csvFile.name
		print fileName
		
		#datadict for column mapping
		dataDictionary = {}
		dataDictionary = (request.POST).dict()
		rowContent = ""

		if "author.csv" in fileName:
			csvFiles['author'] = csvFile
			csvDataBuilder.addCsvData("author.csv", dataDictionary, {'author': csvFile})
			hasFiles[ConferenceType.AUTHOR_ID] = True
		elif "review.csv" in fileName:
			csvFiles['review'] = csvFile
			csvDataBuilder.addCsvData("review.csv", dataDictionary, {'review': csvFile})
			hasFiles[ConferenceType.REVIEW_ID] = True
		elif "submission.csv" in fileName:
			csvFiles['submission'] = csvFile
			csvDataBuilder.addCsvData("submission.csv", dataDictionary, {'submission': csvFile})
			hasFiles[ConferenceType.SUBMISSION_ID] = True
		else:
			print ("ERROR: file should have been rejected by frontend already")
	
	# Combined visualisations
	if (hasFiles[ConferenceType.AUTHOR_ID] and hasFiles[ConferenceType.REVIEW_ID]): # author + review
		csvDataBuilder.addCsvData("author.review", dataDictionary, csvFiles)
	if (hasFiles[ConferenceType.AUTHOR_ID] and hasFiles[ConferenceType.SUBMISSION_ID]): # author + submission
		csvDataBuilder.addCsvData("author.submission", dataDictionary, csvFiles)
	if (hasFiles[ConferenceType.REVIEW_ID] and hasFiles[ConferenceType.SUBMISSION_ID]): # review + submission
		csvDataBuilder.addCsvData("review.submission", dataDictionary, csvFiles)
	if (hasFiles[ConferenceType.AUTHOR_ID] and hasFiles[ConferenceType.REVIEW_ID] and hasFiles[ConferenceType.SUBMISSION_ID]): # author + review + submission
		csvDataBuilder.addCsvData("author.review.submission", dataDictionary, csvFiles)
		
	for i in range(csvDataBuilder.size):
		csvDataBuilder.setOrder(i)
		csvDataBuilder.setInfo(i)
		# print csvDataBuilder.csvDataList[i].order
		#print csvDataBuilder.csvDataList[i].info
	
	rowContent = csvDataBuilder.formatRowContent()
	return rowContent

def saveSession(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	files = str(request['files'])
	data = request['data']
	session = Session.objects.create_session(user, name, date, time, files, data)
	return session.name

def deleteSession(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	session = Session.objects.filter(user=user, name=name, date=date, time=time).first()
	session.delete()
	return session.name

def getSession(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	session = Session.objects.filter(user=user, name=name, date=date, time=time).first()
	return session.data

def getSessionsByEmail(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	sessionsQuerySet = Session.objects.filter(user=user)
	return serializers.serialize('json', list(sessionsQuerySet))

def registerUser(request):
	registerUsername = request['email']
	print registerUsername
	registerPassword = request['password']
	isExist = authenticateUser(registerUsername, registerPassword)
	if isExist:
		return {"isSuccessful": False, "errorMessage": "There already exist a username under that email"}
	else:
		createUser(registerUsername, registerPassword)
	return {"isSuccessful": True}

def loginUser(request):
	loginUsername = request['email']
	loginPassword = request['password']
	isExist = authenticateUser(loginUsername, loginPassword)
	if isExist:
		return {"isSuccessful": True}
	else:
		return {"isSuccessful": False, "errorMessage": "There is no existing user with that username"}

def createUser(username, password):
	user = User.objects.create_user(username, username, password)
	return user.get_username()

def authenticateUser(_username, _password):
    user = authenticate(username=_username, password=_password)
    if user is not None:
        return True
    else:
        return False
