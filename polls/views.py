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
from Constants import *

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData, formatRowContent
from be.models.CsvDataBuilder import CsvDataBuilder
from be.models.CsvData import CsvData
from users.models import Session, SessionManager
from users import *
from users.user import MyUser

# Note: a view is a func taking the HTTP request and returns sth accordingly

def index(request):
	return HttpResponse("Hello, world. You're at the polls index. =)")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request! =)</h1>")

# Note: csr: cross site request, adding this to enable request from localhost
@csrf_exempt
def uploadData(request):
	if request.method == 'POST':
		dataDictionary = {}
		dataDictionary = (request.POST).dict()
		requestType = dataDictionary.get(REQUEST)

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
			registerUser = MyUser(dataDictionary.get(EMAIL), dataDictionary.get(PASSWORD))
			data = registerUser.registerUser()
		elif "login" == requestType:
			loginUser = MyUser(dataDictionary.get(EMAIL), dataDictionary.get(PASSWORD))
			data = loginUser.loginUser()
		else:
			print (INCORRECT_REQUEST_ERROR_MSG)

		if request.POST:
			print ("Now we got the csv file =)")

		return HttpResponse(json.dumps(data))

	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')


def uploadCSVFiles(request):
	hasFiles = [False] * 3 

	csvFiles = {}
	csvFileList = request.FILES.getlist('file')

	csvDataList = []

	for csvFile in csvFileList:
		fileName = csvFile.name
		#datadict for column mapping
		dataDictionary = {}
		dataDictionary = (request.POST).dict()
		rowContent = ""

		if AUTHOR_CSV in fileName:
			csvFiles[AUTHOR] = csvFile
			csvData = CsvData(AUTHOR_CSV, dataDictionary, {AUTHOR: csvFile})
			hasFiles[AUTHOR_ID] = True
		elif REVIEW_CSV in fileName:
			csvFiles[REVIEW] = csvFile
			csvData = CsvData(REVIEW_CSV, dataDictionary, {REVIEW: csvFile})
			hasFiles[REVIEW_ID] = True
		elif SUBMISSION_CSV in fileName:
			csvFiles[SUBMISSION] = csvFile
			csvData = CsvData(SUBMISSION_CSV, dataDictionary, {SUBMISSION: csvFile})
			hasFiles[SUBMISSION_ID] = True
		else:
			print ("ERROR: file should have been rejected by frontend already")
		
		csvDataList.append(csvData)
	
	# Combined visualisations
	if (hasFiles[AUTHOR_ID] and hasFiles[REVIEW_ID]): # author + review
		csvData = CsvData(AUTHOR_REVIEW, dataDictionary, csvFiles)
		csvDataList.append(csvData)
	if (hasFiles[AUTHOR_ID] and hasFiles[SUBMISSION_ID]): # author + submission
		csvData = CsvData(AUTHOR_SUBMISSION, dataDictionary, csvFiles)
		csvDataList.append(csvData)
	if (hasFiles[REVIEW_ID] and hasFiles[SUBMISSION_ID]): # review + submission
		csvData = CsvData(REVIEW_SUBMISSION, dataDictionary, csvFiles)
		csvDataList.append(csvData)
	if (hasFiles[AUTHOR_ID] and hasFiles[REVIEW_ID] and hasFiles[SUBMISSION_ID]): # author + review + submission
		csvData = CsvData(AUTHOR_REVIEW_SUBMISSION, dataDictionary, csvFiles)
		csvDataList.append(csvData)
		
	for i in range(len(csvDataList)):
		csvDataBuilder = CsvDataBuilder(csvDataList[i])
		csvDataBuilder.setOrder()
		csvDataBuilder.setInfo()
		csvDataList[i] = csvDataBuilder.csvData
	
	rowContent = formatRowContent(csvDataList)
	return rowContent

def saveSession(request):
	email = str(request[EMAIL])
	user = User.objects.filter(email=email).first()
	name = str(request[NAME])
	date = str(request[DATE])
	time = str(request[TIME])
	files = str(request['files'])
	data = request['data']
	session = Session.objects.create_session(user, name, date, time, files, data)
	return session.name

def deleteSession(request):
	email = str(request[EMAIL])
	user = User.objects.filter(email=email).first()
	name = str(request[NAME])
	date = str(request[DATE])
	time = str(request[TIME])
	session = Session.objects.filter(user=user, name=name, date=date, time=time).first()
	session.delete()
	return session.name

def getSession(request):
	email = str(request[EMAIL])
	user = User.objects.filter(email=email).first()
	name = str(request[NAME])
	date = str(request[DATE])
	time = str(request[TIME])
	session = Session.objects.filter(user=user, name=name, date=date, time=time).first()
	return session.data

def getSessionsByEmail(request):
	email = str(request[EMAIL])
	user = User.objects.filter(email=email).first()
	sessionsQuerySet = Session.objects.filter(user=user)
	return serializers.serialize('json', list(sessionsQuerySet))
