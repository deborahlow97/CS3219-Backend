import csv
import codecs
import re
from polls import Constants
from collections import Counter
from be.models.CsvExceptions import *
from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, parseCSVFileInverted, isNumber, parseSubmissionTime, appendHasErrorField

# class CalculationUtil:

#     def __init__( self, data, dict ) :
#         self.data = data
#         self.dict = dict

def getTopAuthors(authorData, authorDict):
    result = {}
    authorMap = {}
    for authorInfo in authorData:
        name = str(authorInfo[int(authorDict.get("author.First Name"))] + " " + authorInfo[int(authorDict.get("author.Last Name"))])
        if name not in authorMap:
            authorMap[name] = 1
        else:
            currCount = authorMap[name] + 1
            authorMap[name] = currCount

    topAuthorList = sorted(authorMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    endIndex = getEndIndexForTop10(topAuthorList)
    topAuthorList = topAuthorList[:endIndex]

    result['topAuthors'] = {'labels': [ele[0] for ele in topAuthorList], 'data': [ele[1] for ele in topAuthorList]}
    return result

def getTopCountries(authorData, authorDict):
    result = {}
    countryMap = {}
    for countryInfo in authorData:
        countries = str(countryInfo[int(authorDict.get("author.Country"))])
        if countries not in countryMap:
            countryMap[countries] = 1
        else:
            currCount = countryMap[countries] + 1
            countryMap[countries] = currCount

    topCountryList = sorted(countryMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    endIndex = getEndIndexForTop10(topCountryList)
    topCountryList = topCountryList[:endIndex]
    result['topCountries'] = {'labels': [ele[0] for ele in topCountryList], 'data': [ele[1] for ele in topCountryList]}
    return result

def getTopAffiliations(authorData, authorDict):
    result = {}
    affiliationMap = {}
    for affiliationInfo in authorData:
        affiliations = str(affiliationInfo[int(authorDict.get("author.Organization"))])
        if affiliations not in affiliationMap:
            affiliationMap[affiliations] = 1
        else:
            currCount = affiliationMap[affiliations] + 1
            affiliationMap[affiliations] = currCount

    topAffiliationsList = sorted(affiliationMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    endIndex = getEndIndexForTop10(topAffiliationsList)
    topAffiliationsList = topAffiliationsList[:endIndex]
    result['topCountries'] = {'labels': [ele[0] for ele in topAffiliationsList], 'data': [ele[1] for ele in topAffiliationsList]}
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
            except (ValueError, TypeError) as e:
                return {"Error": "Oops! Value Error occurred. There seems to be an error related to the information in review - field #. Do make sure that only numbers are accepted as field #."}
            
            try:
                score = int(info[int(reviewDict.get("review.Overall Evaluation Score"))])
            except (ValueError, TypeError) as e:
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

def getTopAuthorsByTrackAndAcceptanceRate(submissionData, submissionDict):
    result = {}
    acceptedSubmission = [line for line in submissionData if str(line[int(submissionDict.get("submission.Decision"))]) == 'accept']
    acceptanceRate = float(len(acceptedSubmission)) / len(submissionData)
    topAuthorsByTrack = {}
    acceptanceRateByTrack = {}
    tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in submissionData])
    paperGroupsByTrack = {track : [line for line in submissionData if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
    for track, papers in paperGroupsByTrack.iteritems():
        acceptedPapersPerTrack = [ele for ele in papers if str(ele[int(submissionDict.get("submission.Decision"))]) == 'accept']
        acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)
        acceptedPapersThisTrack = [paper for paper in papers if str(paper[int(submissionDict.get("submission.Decision"))]) == 'accept']
        acceptedAuthorsThisTrack = [str(ele[int(submissionDict.get("submission.Author(s)"))]).replace(" and ", ", ").split(", ") for ele in acceptedPapersThisTrack]
        acceptedAuthorsThisTrack = [ele for item in acceptedAuthorsThisTrack for ele in item]
        topAcceptedAuthorsThisTrack = Counter(acceptedAuthorsThisTrack).most_common()
        topAcceptedAuthorsThisTrack = sorted(topAcceptedAuthorsThisTrack, key=lambda x: x[1], reverse=True)
        endIndex = getEndIndexForTop10(topAcceptedAuthorsThisTrack)
        topAcceptedAuthorsThisTrack = topAcceptedAuthorsThisTrack[:endIndex]

        topAuthorsByTrack[track] = {'names': [ele[0] for ele in topAcceptedAuthorsThisTrack], 'counts': [ele[1] for ele in topAcceptedAuthorsThisTrack]}
    result['topAuthorsByTrack'] = topAuthorsByTrack
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

def getTopAuthorsInfoAR(authorReviewData, combinedDict):
    result = {}
    authorScoreMap = {}
    for Info in authorReviewData:
        name = str(Info[int(combinedDict.get("author.First Name"))] + " " + Info[int(combinedDict.get("author.Last Name"))])
        try:
            score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
        except ValueError as e:
            return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}
        if name not in authorScoreMap:
            authorScoreMap[name] = [score]
        else:
            authorScoreMap[name].append(score)
    #getting average of each author
    for key,value in authorScoreMap.iteritems():
        authorScoreMap[key] = sum(value)/float(len(value))

    authorScoreList = sorted(authorScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    endIndex = getEndIndexForTop10(authorScoreList)
    authorScoreList = authorScoreList[:endIndex]

    nameArr = []
    reviewScoreArr = []
    affiliationArr = []
    countryArr = []
    for Info in authorReviewData:
        nameArr.append(str(Info[int(combinedDict.get("author.First Name"))]) + " " + str(Info[int(combinedDict.get("author.Last Name"))]))
        affiliationArr.append(str(Info[int(combinedDict.get("author.Organization"))]))
        countryArr.append(str(Info[int(combinedDict.get("author.Country"))]))
        try:
            reviewScoreArr.append(int(Info[int(combinedDict.get("review.Overall Evaluation Score"))]))
        except ValueError as e:
            return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}

    infoAndScore = zip(reviewScoreArr, nameArr, affiliationArr, countryArr)[:endIndex]
    infoAndScore.sort(reverse=True)

    result['affiliationDistributionAR'] = {'organization': [ele[2] for ele in infoAndScore],
    'score': [ele[0] for ele in infoAndScore]}
    result['countryDistributionAR'] = {'country': [ele[3] for ele in infoAndScore],                
    'score': [ele[0] for ele in infoAndScore], 'author': [ele[1] for ele in infoAndScore]} 
    result['topAuthorsAR'] =  {'authors': [ele[0] for ele in authorScoreList],'score': [ele[1] for ele in authorScoreList]}
    return result

def getTopCountriesAR(authorReviewData, combinedDict):
    result = {}
    countryScoreMap = {}
    countryScoreList = []
    for Info in authorReviewData:
        try:
            score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
        except ValueError as e:
            return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}
        country = str(Info[int(combinedDict.get("author.Country"))])

        if country not in countryScoreMap:
            countryScoreMap[country] = [score]
        else:
            countryScoreMap[country].append(score)

    #getting average of each country
    for key,value in countryScoreMap.iteritems():
        countryScoreMap[key] = sum(value)/float(len(value))

    countryScoreList = sorted(countryScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)

    endIndex = getEndIndexForTop10(countryScoreList)
    countryScoreList = countryScoreList[:endIndex]
    result['topCountriesAR'] = {'countries': [ele[0] for ele in countryScoreList], 'score': [round(ele[1],3) for ele in countryScoreList]}
    return result

def getTopAffiliationsAR(authorReviewData, combinedDict):
    result = {}
    affiliationScoreMap = {}
    affiliationScoreList = []
    for Info in authorReviewData:
        try:
            score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
        except ValueError as e:
            return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}
        affiliation = str(Info[int(combinedDict.get("author.Organization"))])

        if affiliation not in affiliationScoreMap:
            affiliationScoreMap[affiliation] = [score]
        else:
            affiliationScoreMap[affiliation].append(score)

    #getting average of each country
    for key,value in affiliationScoreMap.iteritems():
        affiliationScoreMap[key] = sum(value)/float(len(value))

    affiliationScoreMap = sorted(affiliationScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    endIndex = getEndIndexForTop10(affiliationScoreList)
    affiliationScoreList = affiliationScoreList[:endIndex]
    result['topAffiliationsAR'] = {'organization': [ele[0] for ele in affiliationScoreList], 'score': [round(ele[1],3) for ele in affiliationScoreList]}
    return result

##################    UTILS    ####################

def getEndIndexForTop10(dataList):
    distinctNum = []
    endIndex = len(dataList)
    for idx in range(len(dataList)):
        if (dataList[idx][1] not in distinctNum):
            distinctNum.append(dataList[idx][1])
        if (len(distinctNum) > 10):
            endIndex = idx-1
            break
    return endIndex