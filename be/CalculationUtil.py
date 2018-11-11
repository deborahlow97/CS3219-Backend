import csv
import codecs
import re
from polls import ConferenceType
from collections import Counter
from be.models.CsvExceptions import *

def getTopAuthors(authorData, authorDict):
    result = {}
    authorList = []
    for authorInfo in authorData:
        authorList.append(
            {'name': str(authorInfo[int(authorDict.get("author.First Name"))]) + " " + str(authorInfo[int(authorDict.get("author.Last Name"))])})

    authors = [ele['name'] for ele in authorList if ele] # adding in the if ele in case of empty strings; same applies below
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

        timeRegex = re.compile(ConferenceType.TIME_REGEX)
        try:
            for time in reviewTime:
                if not timeRegex.match(time):
                    raise TimeDataError( {"error": "Oops! There seems to be an error related to the information in review - time. Do note that only HH:MM format is accepted."})
        except TimeDataError as tde:
            return tde.message

        dateRegex = re.compile(ConferenceType.DATE_REGEX)
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

