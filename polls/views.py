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
	return HttpResponse("goodbye, world. You're at the polls index. =)")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request! =)</h1>")

# Note: csr: cross site request, adding this to enable request from localhost
@csrf_exempt
def uploadCSV(request):
	print ("Inside the upload function!!")
	if request.FILES and request.method == 'POST':
		
		#fileName = []
		authorArray = []
		reviewArray = []
		submissionArray = []

		# csvFile = request.FILES.getlist('file')
		# for files in csvFile:
		# 	fileName.append(str(files.name))

		# print (fileName)

		#nid to fix bug
		csvFile = request.FILES['file']
		print (len(csvFile))
		
		fileName = [str(csvFile.name)]
		#data here
		dataDictionary = {}
		dataDictionary = (request.POST).dict()
		print (dataDictionary)

		rowContent = ""

		if ("author.csv" in fileName) or ("submission.csv" in fileName) or ("review.csv" in fileName):
			if "author.csv" in fileName:
				csvData = Author((request.POST).dict(), csvFile)
				print ("yaya")
			elif "submission.csv" in fileName:
				csvData = Submission((request.POST).dict(), csvFile)
				print ("yayb")
			elif "review.csv" in fileName:
				csvData = Review((request.POST).dict(), csvFile)
				print ("yayc")
			else:
				print ("ERROR: file should have been rejected by frontend already")

			csvData.getOrder()
			rowContent = csvData.getInfo()

		elif "score.csv" in fileName:
			rowContent = getReviewScoreInfo(csvFile)
			print ("yayb")
		else:
			rowContent = returnTestChartData(csvFile)

		print (type(csvFile.name))

		if request.POST:
			# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print ("Now we got the csv file =)")


		return HttpResponse(json.dumps(rowContent))
		# return HttpResponse("Got the CSV file.")
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')