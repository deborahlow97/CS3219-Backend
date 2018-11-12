import csv
import codecs
import re
from polls import Constants
from collections import Counter
from be.models.CsvExceptions import *
from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, parseCSVFileInverted, isNumber, parseSubmissionTime, appendHasErrorField

def getTopAuthors(authorData, authorDict):
    result = {}
    authorList = []
    for authorInfo in authorData:
        authorList.append(
            {'name': str(authorInfo[int(authorDict.get("author.First Name"))]) + " " + str(authorInfo[int(authorDict.get("author.Last Name"))])})

    authors = [ele['name'] for ele in authorList if ele]
    topAuthors = Counter(authors).most_common(10)
    result['topAuthors'] = {'labels': [ele[0] for ele in topAuthors], 'data': [ele[1] for ele in topAuthors]}
    return result

def getTopCountries(authorData, authorDict):
    result = {}
    countryList = []
    for countryInfo in authorData:
        countryList.append(
            {'country': str(countryInfo[int(authorDict.get("author.Country"))])})

    countries = [ele['country'] for ele in countryList if ele]
    topCountries = Counter(countries).most_common(10)
    result['topCountries'] = {'labels': [ele[0] for ele in topCountries], 'data': [ele[1] for ele in topCountries]}
    return result

def getTopAffiliations(authorData, authorDict):
    result = {}
    affiliationList = []
    for affiliationInfo in authorData:
        affiliationList.append(
            {'affiliation': str(affiliationInfo[int(authorDict.get("author.Organization"))])})

    affiliations = [ele['affiliation'] for ele in affiliationList if ele]
    topAffiliations = Counter(affiliations).most_common(10)
    result['topAffiliations'] = {'labels': [ele[0] for ele in topAffiliations], 'data': [ele[1] for ele in topAffiliations]}
    return result

def getReviewTimeSeries(reviewData, reviewDict):
        result = {}
        reviewTime = [str(ele[int(reviewDict.get("review.Time"))]) for ele in reviewData]
        reviewDate = [str(ele[int(reviewDict.get("review.Date"))]) for ele in reviewData]

        timeRegex = re.compile(Constants.TIME_REGEX)
        try:
            for time in reviewTime:
                if not timeRegex.match(time):
                    raise TimeDataError( {"error": "Oops! There seems to be an error related to the information in review - time. Do note that only HH:MM format is accepted."})
        except TimeDataError as tde:
            return tde.message

        dateRegex = re.compile(Constants.DATE_REGEX)
        try:
            for date in reviewDate:
                if not dateRegex.match(date):
                    raise DateDataError( {"error": "Oops! There seems to be an error related to the information in review - date. Do note that only dd/mm/yyyy or d/m/yyyy format is accepted."})
        except DateDataError as dde:
            return dde.message

        reviewDate = Counter(reviewDate)
        lastReviewStamps = sorted([k for k in reviewDate])
        reviewedNumber = [0 for n in range(len(lastReviewStamps))]

        reviewTimeSeries = []
        for index, lastReviewStamps in enumerate(lastReviewStamps):
            if index == 0:
                reviewedNumber[index] = reviewDate[lastReviewStamps]
            else:
                reviewedNumber[index] = reviewDate[lastReviewStamps] + reviewedNumber[index - 1]

            reviewTimeSeries.append({'x': lastReviewStamps, 'y': reviewedNumber[index]})
        result['reviewTimeSeries'] = reviewTimeSeries
        return result

def getScoreDistribution(reviewData, reviewDict):
        result = {}
        submissionIDs = set([str(line[int(reviewDict.get("review.Submission #"))]) for line in reviewData])
        scoreDistributionCounts = [0] * int((3 + 3) / 0.25)
        scoreDistributionLabels = [" ~ "] * len(scoreDistributionCounts)

        for index, col in enumerate(scoreDistributionCounts):
                scoreDistributionLabels[index] = str(-3 + 0.25 * index) + " ~ " + str(-3 + 0.25 * index + 0.25)

        for submissionID in submissionIDs:
                reviews = [str(line[int(reviewDict.get("review.Overall Evaluation Score (ignore)"))]).replace("\r", "") for line in reviewData if str(line[int(reviewDict.get("review.Submission #"))]) == submissionID]
                confidences = [float(review.split("\n")[1].split(": ")[1]) for review in reviews]
                scores = [float(review.split("\n")[0].split(": ")[1]) for review in reviews]
                weightedScore = sum(x * y for x, y in zip(scores, confidences)) / sum(confidences)
                scoreColumn = min(int((weightedScore + 3) / 0.25), 23)
                scoreDistributionCounts[scoreColumn] += 1

        result['scoreDistribution'] = {'labels': scoreDistributionLabels, 'counts': scoreDistributionCounts}
        return result

def getMeanEvScoreByExpertiseLevel(reviewData, reviewDict):
        result = {}
        expertiseScoreMap = {}
        expertise = []
        expertiseScore = []

        for info in reviewData:
            try:
                expertiseLevel = int(info[int(reviewDict.get("review.Field #"))])
            except ValueError:
                return {"Error": "Oops! Value Error occurred. There seems to be an error related to the information in review - field #. Do make sure that only numbers are accepted as field #."}
            try:
                score = int(info[int(reviewDict.get("review.Overall Evaluation Score"))])
            except ValueError as e:
                return {"Error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score. Do make sure that only numbers are accepted as overall evaluation scores."}
            
            if expertiseLevel not in expertiseScoreMap:
                expertiseScoreMap[expertiseLevel] = [score]
            else:
                expertiseScoreMap[expertiseLevel].append(score)

        #getting average of evaluation score given
        for key,value in expertiseScoreMap.iteritems():
            expertiseScoreMap[key] = sum(value)/float(len(value))

        for key, value in sorted(expertiseScoreMap.items()):
            expertise.append(key)
            expertiseScore.append(value)

        result['meanEvaluationScore'] = {'expertise': expertise, 'avgScore': expertiseScore }
        return result

def getSubmissionTimeSeries(submissionData, submissionDict):
	result = {}
	submissionTimes = [parseSubmissionTime(str(ele[int(submissionDict.get("submission.Time Submitted"))])) for ele in submissionData]
	lastEditTimes = [parseSubmissionTime(str(ele[int(submissionDict.get("submission.Time Last Updated"))])) for ele in submissionData]
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

	result['timeSeries'] = timeSeries
	result['lastEditSeries'] = lastEditSeries
	return result

def getTopAcceptedAuthorsAndAcceptanceRate(submissionData, submissionDict):
    result = {}
    acceptedSubmission = [line for line in submissionData if str(line[int(submissionDict.get("submission.Decision"))]) == 'accept']
    acceptanceRate = float(len(acceptedSubmission)) / len(submissionData)
    acceptedAuthors = [str(ele[int(submissionDict.get("submission.Author(s)"))]).replace(" and ", ", ").split(", ") for ele in acceptedSubmission]
    acceptedAuthors = [ele for item in acceptedAuthors for ele in item]
    topAcceptedAuthors = Counter(acceptedAuthors).most_common(10)
    topAcceptedAuthorsMap = {'names': [ele[0] for ele in topAcceptedAuthors], 'counts': [ele[1] for ele in topAcceptedAuthors]}
    result['topAcceptedAuthors'] = topAcceptedAuthorsMap
    result['acceptanceRate'] = acceptanceRate
    return result

def getWordCloudByTrack(submissionData, submissionDict):
	result = {}
	
	tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in submissionData])
	paperGroupsByTrack = {track : [line for line in submissionData if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
	keywordsGroupByTrack = {}
	for track, papers in paperGroupsByTrack.iteritems():
		keywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in papers]
		keywords = [ele for item in keywords for ele in item]
		keywordMap = [[ele[0], ele[1]] for ele in Counter(keywords).most_common(20)]
		keywordsGroupByTrack[track] = keywordMap
	result['keywordsByTrack'] = keywordsGroupByTrack
	return result

def getAcceptanceRateByTrack(submissionData, submissionDict):
	result = {}
	tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in submissionData])
	paperGroupsByTrack = {track : [line for line in submissionData if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
	acceptanceRateByTrack = {}
	for track, papers in paperGroupsByTrack.iteritems():
		acceptedPapersPerTrack = [ele for ele in papers if str(ele[int(submissionDict.get("submission.Decision"))]) == 'accept']
		acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)

	result['acceptanceRateByTrack'] = acceptanceRateByTrack
	return result