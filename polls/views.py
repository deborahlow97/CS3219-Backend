# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

import json

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData

from be.models.CsvDataBuilder import CsvDataBuilder
from be.models.CsvData import CsvData

def checkFormDataType(formDataRequest):
	return 0

def index(request):
	return HttpResponse("Hello, world. You're at the polls index. =)")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request! =)</h1>")


@csrf_exempt
def controlRequest(request):
	print ("Got request!")
	if request.method == 'POST':
    	dataDictionary = {}
        dataDictionary = request.raw_post_data.json.loads()

		if "upload" in dataDictionary.get("request"):
			content = uploadCSV(request)
			return HttpResponse(json.dumps(content))
		elif "save" in dataDictionary.get("request"):
			return 0
		elif "getData" in dataDictionary.get("request"):
			return 0
		elif "getAll" in dataDictionary.get("request"):
			return 0
		else:
			print ("Error")
			return 0  
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')

def uploadCSV(request):
	print ("Inside the upload function!!")
	if request.FILES and request.method == 'POST':
		# TODO: create config file to remove magic numbers
		# file is present ? True : False
		# author - 0 | review - 1 | submission - 2 
		hasFiles = [False] * 3 

		csvFileList = request.FILES.getlist('file')
		csvFiles = {}

		csvDataBuilder = CsvDataBuilder()

		for csvFile in csvFileList:
			print (len(csvFile))
			
			fileName = csvFile.name
			print fileName
			
			print request.POST
			#datadict for column mapping
			dataDictionary = {}
			dataDictionary = (request.POST).dict()
			rowContent = ""

			if "author.csv" in fileName:
				csvFiles['author'] = csvFile
				csvDataBuilder.addCsvData("author.csv", dataDictionary, {'author': csvFile})
				hasFiles[0] = True
				print ("yaya")
			elif "review.csv" in fileName:
				csvFiles['review'] = csvFile
				csvDataBuilder.addCsvData("review.csv", dataDictionary, {'review': csvFile})
				hasFiles[1] = True
				print ("yayb")
			elif "submission.csv" in fileName:
				csvFiles['submission'] = csvFile
				csvDataBuilder.addCsvData("submission.csv", dataDictionary, {'submission': csvFile})
				hasFiles[2] = True
				print ("yayc")
			else:
				print ("ERROR: file should have been rejected by frontend already")
		
		# Combined visualisations
		if (hasFiles[0] and hasFiles[1]): # author + review
			csvDataBuilder.addCsvData("author.review", dataDictionary, csvFiles)
		if (hasFiles[0] and hasFiles[2]): # author + submission
			csvDataBuilder.addCsvData("author.submission", dataDictionary, csvFiles)
		if (hasFiles[1] and hasFiles[2]): # review + submission
			csvDataBuilder.addCsvData("review.submission", dataDictionary, csvFiles)
		if (hasFiles[0] and hasFiles[1] and hasFiles[2]): # author + review + submission
			csvDataBuilder.addCsvData("author.review.submission", dataDictionary, csvFiles)
			
		for i in range(csvDataBuilder.size):
			csvDataBuilder.setOrder(i)
			csvDataBuilder.setInfo(i)
			# print csvDataBuilder.csvDataList[i].order
			# print csvDataBuilder.csvDataList[i].info
		
		rowContent = csvDataBuilder.formatRowContent()
		# print "---"
		# print rowContent
		# print "---"

		if request.POST:
			# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print ("Now we got the csv file =)")

		return HttpResponse(json.dumps(rowContent))
		# return HttpResponse("Got the CSV file.")
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')