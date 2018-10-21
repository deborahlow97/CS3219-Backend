import csv
import codecs
from collections import Counter

from utils import parseCSVFile, testCSVFileFormatMatching, isNumber, parseSubmissionTime

def getSubmissionInfo(inputFile, submissionArray):
	"""
	submission.csv
	data format: 
	submission ID | track ID | track name | title | authors | submit time | last update time | form fields | keywords | decision | notified | reviews sent | abstract
	File has header
	"""

    #['SubmissionIDS', 'TrackID', 'TrackName', 'Title', 'Author', 'TimeSubmitted', 
	# 'TimeLastUpdated', 'FormFields', 'Keywords', 'Decision', 'Notified', 'ReviewSent'
	# 'Abstract']
	parsedResult = {}
	lines = parseCSVFile(inputFile)[1:]
	lines = [ele for ele in lines if ele]
	acceptedSubmission = [line for line in lines if str(line[9]) == 'accept']
	rejectedSubmission = [line for line in lines if str(line[9]) == 'reject']

	acceptanceRate = float(len(acceptedSubmission)) / len(lines)

	submissionTimes = [parseSubmissionTime(str(ele[5])) for ele in lines]
	lastEditTimes = [parseSubmissionTime(str(ele[6])) for ele in lines]
	submissionTimes = Counter(submissionTimes)
	lastEditTimes = Counter(lastEditTimes)
	timeStamps = sorted([k for k in submissionTimes])
	lastEditStamps = sorted([k for k in lastEditTimes])
	submittedNumber = [0 for n in range(len(timeStamps))]
	lastEditNumber = [0 for n in range(len(lastEditStamps))]
	timeSeries = []
	lastEditSeries = []
	for index, timeStamp in enumerate(timeStamps):
		if index == 0:
			submittedNumber[index] = submissionTimes[timeStamp]
		else:
			submittedNumber[index] = submissionTimes[timeStamp] + submittedNumber[index - 1]

		timeSeries.append({'x': timeStamp, 'y': submittedNumber[index]})

	for index, lastEditStamp in enumerate(lastEditStamps):
		if index == 0:
			lastEditNumber[index] = lastEditTimes[lastEditStamp]
		else:
			lastEditNumber[index] = lastEditTimes[lastEditStamp] + lastEditNumber[index - 1]

		lastEditSeries.append({'x': lastEditStamp, 'y': lastEditNumber[index]})

	# timeSeries = {'time': timeStamps, 'number': submittedNumber}
	# lastEditSeries = {'time': lastEditStamps, 'number': lastEditNumber}

	acceptedKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in acceptedSubmission]
	acceptedKeywords = [ele for item in acceptedKeywords for ele in item]
	acceptedKeywordMap = {k : v for k, v in Counter(acceptedKeywords).iteritems()}
	acceptedKeywordList = [[ele[0], ele[1]] for ele in Counter(acceptedKeywords).most_common(20)]

	rejectedKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in rejectedSubmission]
	rejectedKeywords = [ele for item in rejectedKeywords for ele in item]
	rejectedKeywordMap = {k : v for k, v in Counter(rejectedKeywords).iteritems()}
	rejectedKeywordList = [[ele[0], ele[1]] for ele in Counter(rejectedKeywords).most_common(20)]

	allKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in lines]
	allKeywords = [ele for item in allKeywords for ele in item]
	allKeywordMap = {k : v for k, v in Counter(allKeywords).iteritems()}
	allKeywordList = [[ele[0], ele[1]] for ele in Counter(allKeywords).most_common(20)]

	tracks = set([str(ele[2]) for ele in lines])
	paperGroupsByTrack = {track : [line for line in lines if str(line[2]) == track] for track in tracks}
	keywordsGroupByTrack = {}
	acceptanceRateByTrack = {}
	comparableAcceptanceRate = {}
	topAuthorsByTrack = {}

	# Obtained from the JCDL.org website: past conferences
	comparableAcceptanceRate['year'] = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
	comparableAcceptanceRate['Full Papers'] = [0.29, 0.28, 0.27, 0.29, 0.29, 0.30, 0.29, 0.30]
	comparableAcceptanceRate['Short Papers'] = [0.29, 0.37, 0.31, 0.31, 0.32, 0.50, 0.35, 0.32]
	for track, papers in paperGroupsByTrack.iteritems():
		keywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in papers]
		keywords = [ele for item in keywords for ele in item]
		# keywordMap = {k : v for k, v in Counter(keywords).iteritems()}
		keywordMap = [[ele[0], ele[1]] for ele in Counter(keywords).most_common(20)]
		keywordsGroupByTrack[track] = keywordMap

		acceptedPapersPerTrack = [ele for ele in papers if str(ele[9]) == 'accept']
		acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)

		acceptedPapersThisTrack = [paper for paper in papers if str(paper[9]) == 'accept']
		acceptedAuthorsThisTrack = [str(ele[4]).replace(" and ", ", ").split(", ") for ele in acceptedPapersThisTrack]
		acceptedAuthorsThisTrack = [ele for item in acceptedAuthorsThisTrack for ele in item]
		topAcceptedAuthorsThisTrack = Counter(acceptedAuthorsThisTrack).most_common(10)
		topAuthorsByTrack[track] = {'names': [ele[0] for ele in topAcceptedAuthorsThisTrack], 'counts': [ele[1] for ele in topAcceptedAuthorsThisTrack]}

		if track == "Full Papers" or track == "Short Papers":
			comparableAcceptanceRate[track].append(float(len(acceptedPapersPerTrack)) / len(papers))

	acceptedAuthors = [str(ele[4]).replace(" and ", ", ").split(", ") for ele in acceptedSubmission]
	acceptedAuthors = [ele for item in acceptedAuthors for ele in item]
	topAcceptedAuthors = Counter(acceptedAuthors).most_common(10)
	topAcceptedAuthorsMap = {'names': [ele[0] for ele in topAcceptedAuthors], 'counts': [ele[1] for ele in topAcceptedAuthors]}
	# topAcceptedAuthors = {ele[0] : ele[1] for ele in Counter(acceptedAuthors).most_common(10)}

	parsedResult['acceptanceRate'] = acceptanceRate
	parsedResult['overallKeywordMap'] = allKeywordMap
	parsedResult['overallKeywordList'] = allKeywordList
	parsedResult['acceptedKeywordMap'] = acceptedKeywordMap
	parsedResult['acceptedKeywordList'] = acceptedKeywordList
	parsedResult['rejectedKeywordMap'] = rejectedKeywordMap
	parsedResult['rejectedKeywordList'] = rejectedKeywordList
	parsedResult['keywordsByTrack'] = keywordsGroupByTrack
	parsedResult['acceptanceRateByTrack'] = acceptanceRateByTrack
	parsedResult['topAcceptedAuthors'] = topAcceptedAuthorsMap
	parsedResult['topAuthorsByTrack'] = topAuthorsByTrack
	parsedResult['timeSeries'] = timeSeries
	parsedResult['lastEditSeries'] = lastEditSeries
	parsedResult['comparableAcceptanceRate'] = comparableAcceptanceRate

	return {'infoType': 'submission', 'infoData': parsedResult}