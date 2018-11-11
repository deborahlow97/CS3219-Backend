# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

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
		# mycookie = request.COOKIES
		# print "my cookie: "
		# print mycookie
		# myuser = request.user
		# print "myuser: "
		# print myuser

		if request.FILES and "uploadSession" == requestType:
			data = uploadCSVFiles(request)
		elif "getSession" == requestType:
			data = {'result': getSession(dataDictionary)}
		elif "deleteSession" == requestType:
			#todo: add if case when error
			data = {'result': deleteSession(dataDictionary)}
		elif "saveSession" == requestType:
			#todo: add if case when error
			data = {'result': saveSession(dataDictionary)}
		elif "getAll" == requestType:
			data = 0
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
	# file is present ? True : False
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
		# print dataDictionary
		# print "*************"
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
	session_name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	file_names = str(request['files'])
	data = str(request['data'])
	session = Session.objects.create_session(user, session_name, date, time, file_names, data)
	return session.session_name

def deleteSession(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	session_name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	session = Session.objects.filter(user=user, session_name=session_name, date=date, time=time)
	session.delete()
	return session.session_name

def getSession(request):
	email = str(request['email'])
	user = User.objects.filter(email=email).first()
	session_name = str(request['name'])
	date = str(request['date'])
	time = str(request['time'])
	session = Session.objects.filter(user=user, session_name=session_name, date=date, time=time)
	return session.data

def registerUser(request):
	registerUsername = request['username']
	registerPassword = request['password']
	isExist = authenticateUser(registerUsername, registerPassword)
	if isExist:
		return { "Error": "There already exist a username under that email"}
	else:
		createUser(registerUsername, registerPassword)
	return {"User successfully registered!"}

def loginUser(request):
	loginUsername = request['username']
	loginPassword = request['password']
	isExist = authenticateUser(loginUsername, loginPassword)
	if isExist:
		print("TODO")
		return 0
		#DO SMTH - LOGIN
	else:
		return { "Error": "There is no existing user with that username"}

def createUser(username, password):
	user = User.objects.create_user(username, username, password)
	return user.get_username()

def authenticateUser(_username, _password): #might not be working atm, dk are we supposed to put in pw too?
    user = authenticate(username=_username, password=_password)
    if user is not None:
        return True
    else:
        return False
