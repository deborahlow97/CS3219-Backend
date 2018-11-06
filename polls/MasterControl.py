# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

import json

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData

from views import uploadCSV
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

		csvFileList = request.FILES.getlist('file')
		csvFiles = {}
        dataDictionary = {}
        dataDictionary = request.raw_post_data.json.loads()

        if (dataDictionary.get("request") == "upload"):
            content = uploadCSV(request)
            return HttpResponse(json.dumps(content))
        elif (dataDictionary.get("request") == "save"):
            return 0
        elif (dataDictionary.get("request") == "getData"):
            return 0
        elif (dataDictionary.get("request") == "getAll"):
            return 0
        else:
            print "Error"
            return 0
            
	else:
		print ("Not found the file! =(")
		return HttpResponseNotFound('Page not found for CSV =(')