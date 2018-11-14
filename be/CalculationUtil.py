import csv
import codecs
import re
from polls.Constants import *
from collections import Counter
from be.models.CsvExceptions import *
from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, isNumber, parseSubmissionTime, appendHasErrorField

class CalculationUtil:
    ##################    AUTHOR INFO    ##################
    def getTopAuthors(self, authorData, authorDict):
        try:
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
            endIndex = self.getEndIndexForTop10(topAuthorList)
            topAuthorList = topAuthorList[:endIndex]

            result['topAuthors'] = {'labels': [ele[0] for ele in topAuthorList], 'data': [ele[1] for ele in topAuthorList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopCountries(self, authorData, authorDict):
        try:
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
            endIndex = self.getEndIndexForTop10(topCountryList)
            topCountryList = topCountryList[:endIndex]
            result['topCountries'] = {'labels': [ele[0] for ele in topCountryList], 'data': [ele[1] for ele in topCountryList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopAffiliations(self, authorData, authorDict):
        try:
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
            endIndex = self.getEndIndexForTop10(topAffiliationsList)
            topAffiliationsList = topAffiliationsList[:endIndex]
            result['topAffiliations'] = {'labels': [ele[0] for ele in topAffiliationsList], 'data': [ele[1] for ele in topAffiliationsList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    ##################    REVIEW INFO    ##################
    def getReviewTimeSeries(self, reviewData, reviewDict):
        try:
            result = {}
            reviewTime = [str(ele[int(reviewDict.get("review.Time"))]) for ele in reviewData]
            reviewDate = [str(ele[int(reviewDict.get("review.Date"))]) for ele in reviewData]

            timeRegex = re.compile(TIME_REGEX)
            try:
                for time in reviewTime:
                    if not timeRegex.match(time):
                        raise TimeDataError( {ERROR: TIME_FORMAT_ERROR_MSG })
            except TimeDataError as tde:
                return tde.message

            dateRegex = re.compile(DATE_REGEX)
            try:
                for date in reviewDate:
                    if not dateRegex.match(date):
                        raise DateDataError( {ERROR: DATE_FORMAT_ERROR_MSG })
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
        except:
            return {ERROR: ERROR_MSG}

        return result

    def getScoreDistribution(self, reviewData, reviewDict):
        try:
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
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getMeanEvScoreByExpertiseLevel(self, reviewData, reviewDict):
        try:
            result = {}
            expertiseScoreMap = {}
            expertise = []
            expertiseScore = []

            for info in reviewData:
                try:
                    expertiseLevel = int(info[int(reviewDict.get("review.Field #"))])
                except (ValueError, TypeError) as e:
                    return {ERROR: REVIEW_FIELD_NO_ERROR_MSG}
                
                try:
                    score = int(info[int(reviewDict.get("review.Overall Evaluation Score"))])
                except (ValueError, TypeError) as e:
                    return {ERROR: REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG}
                
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
        except:
            return {ERROR: ERROR_MSG}
        
        return result

    ##################    SUBMISSION INFO    ##################
    def getSubmissionTimeSeries(self, submissionData, submissionDict):
        try:
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
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopAuthorsByTrackAndAcceptanceRate(self, submissionData, submissionDict):
        try:
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
                endIndex = self.getEndIndexForTop10(topAcceptedAuthorsThisTrack)
                topAcceptedAuthorsThisTrack = topAcceptedAuthorsThisTrack[:endIndex]
                topAuthorsByTrack[track] = {'names': [ele[0] for ele in topAcceptedAuthorsThisTrack], 'counts': [ele[1] for ele in topAcceptedAuthorsThisTrack]}
            
            result['topAuthorsByTrack'] = topAuthorsByTrack
            result['acceptanceRate'] = acceptanceRate
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getWordCloudByTrack(self, submissionData, submissionDict):
        result = {}
        try:
            tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in submissionData])
            paperGroupsByTrack = {track : [line for line in submissionData if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
            keywordsGroupByTrack = {}
            for track, papers in paperGroupsByTrack.iteritems():
                keywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in papers]
                keywords = [ele for item in keywords for ele in item]
                keywordMap = [[ele[0], ele[1]] for ele in Counter(keywords).most_common(20)]
                keywordsGroupByTrack[track] = keywordMap
            result['keywordsByTrack'] = keywordsGroupByTrack
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getAcceptanceRateByTrack(self, submissionData, submissionDict):
        result = {}
        try:
            tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in submissionData])
            paperGroupsByTrack = {track : [line for line in submissionData if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
            acceptanceRateByTrack = {}
            for track, papers in paperGroupsByTrack.iteritems():
                acceptedPapersPerTrack = [ele for ele in papers if str(ele[int(submissionDict.get("submission.Decision"))]) == 'accept']
                acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)

            result['acceptanceRateByTrack'] = acceptanceRateByTrack
        except:
            return {ERROR: ERROR_MSG}
        return result

    ##################    AUTHOR REVIEW INFO    ##################
    def getTopAuthorsInfoAR(self, authorReviewData, combinedDict):
        result = {}
        try:
            authorScoreMap = {}
            for Info in authorReviewData:
                name = str(Info[int(combinedDict.get("author.First Name"))] + " " + Info[int(combinedDict.get("author.Last Name"))])
                try:
                    score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
                except ValueError as e:
                    return {"error": REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG}
                if name not in authorScoreMap:
                    authorScoreMap[name] = [score]
                else:
                    authorScoreMap[name].append(score)
            #getting average of each author
            for key,value in authorScoreMap.iteritems():
                authorScoreMap[key] = sum(value)/float(len(value))

            authorScoreList = sorted(authorScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
            endIndex = self.getEndIndexForTop10(authorScoreList)
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
                    return {"error": REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG}

            infoAndScore = zip(reviewScoreArr, nameArr, affiliationArr, countryArr)[:endIndex]
            infoAndScore.sort(reverse=True)

            result['affiliationDistributionAR'] = {'organization': [ele[2] for ele in infoAndScore],
            'score': [ele[0] for ele in infoAndScore]}
            result['countryDistributionAR'] = {'country': [ele[3] for ele in infoAndScore],                
            'score': [ele[0] for ele in infoAndScore], 'author': [ele[1] for ele in infoAndScore]} 
            result['topAuthorsAR'] =  {'authors': [ele[0] for ele in authorScoreList],'score': [ele[1] for ele in authorScoreList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopCountriesAR(self, authorReviewData, combinedDict):
        result = {}
        countryScoreMap = {}
        countryScoreList = []
        try:
            for Info in authorReviewData:
                try:
                    score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
                except ValueError as e:
                    return {"error": REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG}
                country = str(Info[int(combinedDict.get("author.Country"))])

                if country not in countryScoreMap:
                    countryScoreMap[country] = [score]
                else:
                    countryScoreMap[country].append(score)

            #getting average of each country
            for key,value in countryScoreMap.iteritems():
                countryScoreMap[key] = sum(value)/float(len(value))

            countryScoreList = sorted(countryScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)

            endIndex = self.getEndIndexForTop10(countryScoreList)
            countryScoreList = countryScoreList[:endIndex]
            result['topCountriesAR'] = {'countries': [ele[0] for ele in countryScoreList], 'score': [round(ele[1],3) for ele in countryScoreList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopAffiliationsAR(self, authorReviewData, combinedDict):
        result = {}
        affiliationScoreMap = {}
        affiliationScoreList = []
        try:
            for Info in authorReviewData:
                try:
                    score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
                except ValueError as e:
                    return {"error": REVIEW_OVERALL_EVAL_SCORE_ERROR_MSG}
                affiliation = str(Info[int(combinedDict.get("author.Organization"))])

                if affiliation not in affiliationScoreMap:
                    affiliationScoreMap[affiliation] = [score]
                else:
                    affiliationScoreMap[affiliation].append(score)

            #getting average of each country
            for key,value in affiliationScoreMap.iteritems():
                affiliationScoreMap[key] = sum(value)/float(len(value))

            affiliationScoreList = sorted(affiliationScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)
            endIndex = self.getEndIndexForTop10(affiliationScoreList)
            affiliationScoreList = affiliationScoreList[:endIndex]
            result['topAffiliationsAR'] = {'organization': [ele[0] for ele in affiliationScoreList], 'score': [round(ele[1],3) for ele in affiliationScoreList]}
        
        except:
            return {ERROR: ERROR_MSG}
        return result

    ##################    AUTHOR SUBMISSION INFO    ##################
    def getTopCountriesAS(self, authorSubmissionData, combinedDict):
        result = {}
        acceptedCountriesList = []
        try:
            for ele in authorSubmissionData:
                if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept':
                    acceptedCountriesList.append(ele[int(combinedDict.get("author.Country"))])
            topCountriesList = dict(Counter(acceptedCountriesList))
            topCountriesList = sorted(topCountriesList.iteritems(), key=lambda (k,v): (v,k), reverse=True)

            distinctNumDecisions = []
            endIndex = len(topCountriesList)
            for i in range(len(topCountriesList)):
                if (topCountriesList[i] not in distinctNumDecisions):
                    distinctNumDecisions.append(topCountriesList[i])
                if (len(distinctNumDecisions) > 10):
                    #top 10
                    endIndex = i-1
                    break
            
            topCountriesList = topCountriesList[:endIndex]
            
            result['topCountriesAS'] = {'labels': [key for key, value in topCountriesList], 'data': [value for key, value in topCountriesList]}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getTopAffiliationsAS(self, authorSubmissionData, combinedDict):
        result = {}
        decisionBasedOnTopAffiliations = []
        topAffiliationDataForTrack = []
        try:
            tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in authorSubmissionData]).keys())
            
            for track in tracks:
                acceptedSubmissionsByAffiliationAndTrack = []
                for ele in authorSubmissionData:
                    if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept' and str(ele[int(combinedDict.get("submission.Track Name"))]) == track:
                        acceptedSubmissionsByAffiliationAndTrack.append(ele[int(combinedDict.get("author.Organization"))])
                topAffiliationsList = dict(Counter(acceptedSubmissionsByAffiliationAndTrack))
                topAffiliationsList = sorted(topAffiliationsList.iteritems(), key=lambda (k,v): (v,k), reverse=True)
                
                distinctNumDecisions = []
                endIndex = len(topAffiliationsList)
                for i in range(len(topAffiliationsList)):
                    if (topAffiliationsList[i] not in distinctNumDecisions):
                        distinctNumDecisions.append(topAffiliationsList[i])
                    if (len(distinctNumDecisions) > 10):
                        endIndex = i-1
                        break

                topAffiliationsList = topAffiliationsList[:endIndex]
                topAffiliationDataForTrack.append([key for key, value in topAffiliationsList])
                topAffiliationDataForTrack.append([value for key, value in topAffiliationsList])
                decisionBasedOnTopAffiliations.append(topAffiliationDataForTrack)

            result['topAffiliationsAS'] = {'labels':tracks, 'data': decisionBasedOnTopAffiliations}
        except:
            return {ERROR: ERROR_MSG}
        return result

    ##################    SUBMISSION REVIEW INFO    ##################
    def getExpertiseSR(self, submissionReviewData, combinedDict):
        result = {}
        try:
            tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in submissionReviewData]).keys())
            expertiseByTrack = dict()
            for track in tracks:
                dataListForCurrentTrack = []
                for line in submissionReviewData:
                    if (line[int(combinedDict.get("submission.Track Name"))] == track):
                        dataListForCurrentTrack.append(line[int(combinedDict.get("review.Field #"))])
                expertiseByTrack[track] = dict(Counter(dataListForCurrentTrack))
            result['expertiseSR'] = {'labels': tracks, 'data': list(expertiseByTrack.values())}
        except:
            return {ERROR: ERROR_MSG}
        return result

    def getAverageScoreSR(self, submissionReviewData, combinedDict):
        try:
            result = {}
            tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in submissionReviewData]).keys())
            meanScoreByTrack = dict()
            for track in tracks:
                scoreListForCurrentTrack = []
                for line in submissionReviewData:
                    if (line[int(combinedDict.get("submission.Track Name"))] == track):
                        scoreListForCurrentTrack.append(line[int(combinedDict.get("review.Overall Evaluation Score"))])
                meanScoreByTrack[track] = sum([int(ele) for ele in scoreListForCurrentTrack])/len(scoreListForCurrentTrack)

            result['averageScoreSR'] = {'labels': tracks, 'data': list(meanScoreByTrack.values())}
        except:
            return {ERROR: ERROR_MSG}
        return result
        
    ##################    UTILS    ##################

    def getEndIndexForTop10(self, dataList):
        distinctNum = []
        endIndex = len(dataList)
        for idx in range(len(dataList)):
            if (dataList[idx][1] not in distinctNum):
                distinctNum.append(dataList[idx][1])
            if (len(distinctNum) > 10):
                endIndex = idx-1
                break
        return endIndex