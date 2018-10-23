# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

import json

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData
from getInsight import parseAuthorCSVFile

from be.models.CsvData import CsvData
from be.models.Author import Author
from be.models.Review import Review
from be.models.Submission import Submission

# Create your views here.
# Note: a view is a func taking the HTTP request and returns sth accordingly

def index(request):
	return HttpResponse("Hello, world. You're at the polls index. =)")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request! =)</h1>")

# Note: csr: cross site request, adding this to enable request from localhost
@csrf_exempt
def uploadCSV(request):
	print ("Inside the upload function!!")
	if request.FILES and request.method == 'POST':
		
		authorArray = []
		reviewArray = []
		submissionArray = []

		# TODO: create config file to remove magic numbers
		# file is present ? True : False
		# author - 0 | review - 1 | submission - 2 
		hasFiles = [False] * 3 

		csvFileList = request.FILES.getlist('file')
		print (csvFileList)
		for csvFile in csvFileList:
			print (len(csvFile))
			
			fileName = csvFile.name
			print fileName
			
			#datadict for column mapping
			dataDictionary = {}
			dataDictionary = (request.POST).dict()
			print dataDictionary

			rowContent = ""

			if "author.csv" in fileName:
				csvData = Author(dataDictionary, csvFile)
				hasFiles[0] = True
				print ("yaya")
			elif "review.csv" in fileName:
				csvData = Review(dataDictionary, csvFile)
				hasFiles[1] = True
				print ("yayb")
			elif "submission.csv" in fileName:
				csvData = Submission(dataDictionary, csvFile)
				hasFiles[2] = True
				print ("yayc")
			else:
				print ("ERROR: file should have been rejected by frontend already")

			csvData.getOrder()
			rowContent = csvData.getInfo()
		
		# TODO: find the combined visualisations
		if (hasFiles[0] and hasFiles[1]): # author + review
			print ("author + review")
		if (hasFiles[0] and hasFiles[2]): # author + submission
			print ("author + submission")
		if (hasFiles[1] and hasFiles[2]): # review + submission
			print ("review + submission")
		if (hasFiles[0] and hasFiles[1] and hasFiles[2]): # author + review + submission
			print ("author + review + submission")
			
		if request.POST:
			# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print ("Now we got the csv file =)")

		return HttpResponse(json.dumps(rowContent))
		# return HttpResponse("Got the CSV file.")
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')