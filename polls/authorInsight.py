import csv
import codecs
from collections import Counter

from utils import parseCSVFile, parseCSVFileInverted, testCSVFileFormatMatching, isNumber, parseSubmissionTime

def getAuthorInfo(inputFile, authorArray):
	"""
	author.csv: header row, author names with affiliations, countries, emails
	data format:
	submission ID | f name | s name | email | country | affiliation | page | person ID | corresponding?
	"""

	parsedResult = {}
	#Case 1: Header given in CSV File - array is empty
	if not authorArray:
		lines = parseCSVFile(inputFile)[1:]
		lines = [ele for ele in lines if ele]
	#Case 2: Header not given in CSV file 
	else:
		lines = parseCSVFile(inputFile)
		lines = [ele for ele in lines if ele]

	#debugging purpose
	#invertedLines = parseCSVFileInverted(lines)

	authorList = []
	# for x in lines:
	# 	print(x)
	print len(lines)
	#debugging purpose
	#for y in invertedLines:
	#	print (y)

	for authorInfo in lines:
		#authorInfo = line.replace("\"", "").split(",")
		authorList.append(
			{'name': str(authorInfo[int(authorArray.index("FirstName"))]) + " " + str(authorInfo[int(authorArray.index("LastName"))]),
			'country': str(authorInfo[int(authorArray.index("Country"))]),
			'affiliation': str(authorInfo[int(authorArray.index("Organization"))])})
	
	# if not authorArray:
	authors = [ele['name'] for ele in authorList if ele] # adding in the if ele in case of empty strings; same applies below
	topAuthors = Counter(authors).most_common(10)
	parsedResult['topAuthors'] = {'labels': [ele[0] for ele in topAuthors], 'data': [ele[1] for ele in topAuthors]}

	# for x in parsedResult:
	# 	for y in x['topAuthors']:
	# 		print str(y['labels']) + " aaa " + str(y['data'])

	countries = [ele['country'] for ele in authorList if ele]
	topCountries = Counter(countries).most_common(10)
	parsedResult['topCountries'] = {'labels': [ele[0] for ele in topCountries], 'data': [ele[1] for ele in topCountries]}

	affiliations = [ele['affiliation'] for ele in authorList if ele]
	topAffiliations = Counter(affiliations).most_common(10)
	parsedResult['topAffiliations'] = {'labels': [ele[0] for ele in topAffiliations], 'data': [ele[1] for ele in topAffiliations]}

	return {'infoType': 'author', 'infoData': parsedResult}
