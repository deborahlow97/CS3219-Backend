# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

import json

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData
from getInsight import parseAuthorCSVFile
from reviewScoreInsight import getReviewScoreInfo
from authorInsight import getAuthorInfo
from reviewInsight import getReviewInfo
from submissionInsight import getSubmissionInfo

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
	if request.FILES :
		csvFile = request.FILES['file']
		print csvFile
		# csvFile = []
		# fileName = []
		# for f in request.FILES['file']:
		# 	fileName.append(str(f.name))
		# #request.FILES['file']
		# # TODO: Get header data here! store it in a array, currently using a dummy arr

		# #Contents of dummy array
		dummyArray = ["SubmissionID", "FirstName", "LastName",
		"Email", "Country", "Organization", "Webpage", "PersonID", "Corresponding"];
		# #fileName = []
		# #for fn in csvFile:
		# #	fileName.append(str(fn.name))
		fileName = [str(csvFile.name)]
		rowContent = ""

		if "author.csv" in fileName:
			rowContent = getAuthorInfo(csvFile, dummyArray)
			print ("yaya")
		elif "score.csv" in fileName:
			rowContent = getReviewScoreInfo(csvFile)
			print ("yayb")
		elif "review.csv" in fileName:
			rowContent = getReviewInfo(csvFile)
			print ("yayc")
		elif "submission.csv" in fileName:
			rowContent = getSubmissionInfo(csvFile)
			print ("yayd")
		else:
			rowContent = returnTestChartData(csvFile)

		print ("yay")
		#print (type(csvFile.name))

		if request.POST:
	# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print ("Now we got the csv file =)")


		return HttpResponse(json.dumps(rowContent))
		# return HttpResponse("Got the CSV file.")
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')