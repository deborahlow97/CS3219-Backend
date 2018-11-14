import csv
import codecs
import re
import Constants
from be.models.CsvExceptions import *

from django.http import QueryDict

def isNumber(inputStr):
	try:
		float(inputStr)
		return True
	except ValueError:
		return False

def appendHasErrorField(info):
	if "error" not in info:
		info.update({"error": ""})
	return info

def getLinesFromInputFile(inputFile, hasHeader):
	#Case 1: Header given. hasHeader == true
	if hasHeader:
		lines = parseCSVFile(inputFile)[1:]
	#Case 2: Header not given in CSV file 
	else:
		lines = parseCSVFile(inputFile)
    
	#change list of list to -> remove empty rows
	lines = [ele for ele in lines if ele]
	return lines

def combineOrderDict(dict1, dict2):
	# order of dict1, dict2 matters! should match with combineLinesOnKey
	dict3 = dict(dict1)
	size = len(dict1) - 1
	for key in dict2.keys():
		if (".HasHeader" not in key):
			dict2[key] = dict2[key] + size
	dict3.update(dict2)
	return dict3
	
def combineLinesOnKey(lines1, lines2, key1, key2, dict1, dict2):
	combinedLines = []
	for ele1 in lines1:
		for ele2 in lines2:
			if (ele1[dict1.get(key1)] == ele2[dict2.get(key2)]):
				combinedLines.append(ele1 + ele2)
				lines2.remove(ele2)
	return combinedLines

def parseCSVFile(inputFile):
	"""
	Parse the uploaded CSV file
	assuming that the uploaded file is of Excel CSV format: allowing multilines in one cell, use double quote to include such cells
	
	Inputs: Django uploaded file 

	Returns: list of lists (inner list represent each row)
	"""

	csvFile = inputFile
	print inputFile
	# print ("startSniffing")
	# dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvFile, "utf-8").read(1024))
	# print ("endSniffing")
	csvFile.open()
	# reader = csv.reader(codecs.EncodedFile(csvFile, "utf-8"), delimiter=',', dialect=dialect)
	reader = csv.reader(codecs.EncodedFile(csvFile, "utf-8"), delimiter=',', dialect='excel')
	rowResults = [row for row in reader]
	# print (len(rowResults))
	return rowResults

def parseCSVFileInverted(input2DArr):
	#returns inverted table
	return zip(*input2DArr)

def parseSubmissionTime(timeStr):
	dateAndTimeRegex = re.compile(Constants.DATE_AND_TIME_REGEX)
	try:
		if not dateAndTimeRegex.match(timeStr):
			raise DateAndTimeDataError({"Error": "Oops! There seems to be an error related to the information in submission - time submitted or time last updated. Do note that only yyyy-mm-dd HH:MM format is accepted."})
	except DateAndTimeDataError as datde:
		return datde

	date = timeStr.split("\\s+")[0]
	return date

def returnTestChartData(inputFile):
	"""
	Just return dummy data for testing the Charts construction
	"""
	data = {}
	data["year"] = [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999]
	data["inCitations"] = [12, 18, 34, 45, 23, 99, 65, 45, 55, 90]
	data["outCitations"] = [34, 41, 9, 23, 39, 74, 35, 12, 90, 44]
	return {'infoType': 'dummy', 'infoData': data}

def parseCSVFileFromDjangoFile(inputFile):
	parsedResult = {}
	fileData = inputFile.read().decode("utf-8")
	lines = fileData.split("\n")
	#print lines[0]
	headerRow = lines[0]
	secondRow = lines[1]
			
	hasHeader = False
	for index, ele in enumerate(headerRow):
		ele2 = float(secondRow[index]) if isNumber(secondRow[index]) else secondRow[index]
		if type(ele) != type(ele2):
			hasHeader = True
			break

	contentRow = secondRow if hasHeader else headerRow
	# contentRow = secondRow
	# Testing with the first row content
	for index, ele in enumerate(contentRow):
		parsedResult["entry" + str(index + 1)] = ele

	return parsedResult

def setOfValidHeaders(typeOfFile):
	AuthorHeaders = {"Last Name", "First Name", "Webpage", "Email", "Submission #", "Country", "Corresponding", "Person #", "Organization"}
	ReviewHeaders = {"Overall Evaluation Score (ignore)", "Subreviewer Info 2 (ignore)", "Review #", "Comments", "Date", "Submission #",
	"Overall Evaluation Score", "Subreviewer Info 3 (ignore)", "Subreviewer Info 1 (ignore)", "Subreviewer Info 4 (ignore)", "Field #", "Time", "Reviewer Name", "Recommendation for Best Paper", "Review Assignment #"}
	SubmissionHeaders = {"Review Sent", "Title", "Abstract", "Author(s)", "Keyword(s)", "Time Submitted", "Form Fields", "Time Last Updated", "Notified", "Submission #", "Track #", "Track Name", "Decision"}
	if "author" in typeOfFile:
		return AuthorHeaders
	elif "review" in typeOfFile:
		return ReviewHeaders
	elif "submission" in typeOfFile:
		return SubmissionHeaders
	else:
		return {}

def formatRowContent(csvDataList):
	rowContent = {}

	infoType = []
	infoData = {}
	for i in range(len(csvDataList)):
		csvData = csvDataList[i]
		if (".csv" in csvData.infoType):
			infoType.append(csvData.infoType)
		infoData.update(csvData.info)

	rowContent['infoType'] = infoType
	rowContent['infoData'] = appendHasErrorField(infoData)
	return rowContent

if __name__ == "__main__":
	parseCSVFile("review.csv")