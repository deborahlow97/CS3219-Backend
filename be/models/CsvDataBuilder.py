from CsvData import CsvData

import csv
import codecs
import re
from be.CalculationUtil import *
from CsvExceptions import *
import polls.Constants
from collections import Counter
from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, parseCSVFileInverted, isNumber, parseSubmissionTime, appendHasErrorField

'''
Represents a builder class to build csv data from an uploaded csv file
'''
class CsvDataBuilder:
    def __init__(self):
        self.csvDataList = []
        self.size = 0

    def addCsvData(self, infoType, dataDictionary, inputFiles):
        csvData = CsvData(infoType, dataDictionary, inputFiles)
        self.csvDataList.append(csvData)
        self.size += 1

    def setOrder(self, index):
        order = self.getOrder(index)
        self.csvDataList[index].setOrder(order)
        
    def getOrder(self, index):
        order = {}
        type = self.csvDataList[index].infoType
        if type == "author.csv":
            order = self.getAuthorOrder(index)
        elif type == "review.csv":
            order = self.getReviewOrder(index)
        elif type == "submission.csv":
            order = self.getSubmissionOrder(index)
        elif type == "author.review":
            print ("author + review")
            order = combineOrderDict(self.getAuthorOrder(index), self.getReviewOrder(index))
        elif type == "author.submission":
            print ("author + submission")
            order = combineOrderDict(self.getAuthorOrder(index), self.getSubmissionOrder(index))
        elif type == "review.submission":
            print ("submission + review")
            order = combineOrderDict(self.getReviewOrder(index), self.getSubmissionOrder(index))
        elif type == "author.review.submission":
            # Not doing
            print ("author + review + submission")
        else:
            print ("ERROR: No such type")
        return order

    def setInfo(self, index):
        info = self.getInfo(index)
        self.csvDataList[index].setInfo(info)

    def getInfo(self, index):
        info = {}
        type = self.csvDataList[index].infoType
        if type == "author.csv":
            info = self.getAuthorInfo(index)
        elif type == "review.csv":
            info = self.getReviewInfo(index)
        elif type == "submission.csv":
            info = self.getSubmissionInfo(index)
        elif type == "author.review":
            info = self.getAuthorReviewInfo(index)
            print ("author + review")
        elif type == "author.submission":
            info = self.getAuthorSubmissionInfo(index)
            print ("author + submission")
        elif type == "review.submission":
            info = self.getReviewSubmissionInfo(index)
            print ("submission + review")
        elif type == "author.review.submission":
            # Not doing
            info = {}
            print ("author + review + submission")            
        else:
            print ("ERROR: No such info")
        return info
            
    def formatRowContent(self):
        rowContent = {}

        infoType = []
        infoData = {}
        for i in range(self.size):
            csvData = self.csvDataList[i]
            # print csvData.infoType
            if (".csv" in csvData.infoType):
                infoType.append(csvData.infoType)
            infoData.update(csvData.info)

        rowContent['infoType'] = infoType
        rowContent['infoData'] = appendHasErrorField(infoData)
        return rowContent

    def getAuthorOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        authorDict = {}

        for key, value in dataDictionary.iteritems():
            if "author.HasHeader" in key:
                authorDict.update({str(key): bool(value)})
            elif "author." in key:
                authorDict.update({str(key): int(value)})
                
        return authorDict

    def getReviewOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        reviewDict = {}

        for key, value in dataDictionary.iteritems():
            if "review.HasHeader" in key:
                reviewDict.update({str(key): bool(value)})
            elif "review." in key:
                reviewDict.update({str(key): int(value)})

        return reviewDict

    def getSubmissionOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        submissionDict = {}

        for key, value in dataDictionary.iteritems():
            if "submission.HasHeader" in key:
                submissionDict.update({str(key): bool(value)})
            elif "submission." in key:

                submissionDict.update({str(key): int(value)})

        return submissionDict

    '''
    ==================================== GET INFO METHODS =====================================
    '''
    def getAuthorInfo(self, index, dict = None):
        if (dict is None):
            authorDict = self.csvDataList[index].order
        else:
            authorDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('author')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(authorDict.get("author.HasHeader")))

        parsedResult.update(getTopAuthors(lines, authorDict))
        parsedResult.update(getTopCountries(lines, authorDict))
        parsedResult.update(getTopAffiliations(lines, authorDict))
        return parsedResult

    def getReviewInfo(self, index, dict = None):
        if (dict is None):
            reviewDict = self.csvDataList[index].order
        else:
            reviewDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('review')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(reviewDict.get("review.HasHeader")))

        parsedResult.update(getReviewTimeSeries(lines, reviewDict))
        parsedResult.update(getScoreDistribution(lines, reviewDict))
        parsedResult.update(getMeanEvScoreByExpertiseLevel(lines, reviewDict))

        return parsedResult
        
    def getSubmissionInfo(self, index, dict = None):
        if (dict is None):
            submissionDict = self.csvDataList[index].order
        else:
            submissionDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('submission')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(submissionDict.get("submission.HasHeader")))
        parsedResult.update(getTopAuthorsByTrackAndAcceptanceRate(lines, submissionDict))
        parsedResult.update(getWordCloudByTrack(lines, submissionDict))
        parsedResult.update(getSubmissionTimeSeries(lines, submissionDict))
        parsedResult.update(getAcceptanceRateByTrack(lines, submissionDict))
        return parsedResult

    def getAuthorReviewInfo(self, index):
        authorDict = self.getAuthorOrder(index)
        reviewDict = self.getReviewOrder(index)
        combinedDict = self.csvDataList[index].order
        inputFile1 = self.csvDataList[index].csvFiles.get('author')
        inputFile2 = self.csvDataList[index].csvFiles.get('review')

        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get("author.HasHeader")))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get("review.HasHeader")))
        combinedLines = combineLinesOnKey(lines1, lines2, "author.Submission #", "review.Submission #", authorDict, reviewDict)
        parsedResult = {}

        nameArr = []
        reviewScoreArr = []
        affiliationArr = []
        countryArr = []
        for Info in combinedLines:
            
            nameArr.append(str(Info[int(combinedDict.get("author.First Name"))]) + " " + str(Info[int(combinedDict.get("author.Last Name"))]))
            affiliationArr.append(str(Info[int(combinedDict.get("author.Organization"))]))
            countryArr.append(str(Info[int(combinedDict.get("author.Country"))]))
            try:
                reviewScoreArr.append(int(Info[int(combinedDict.get("review.Overall Evaluation Score"))]))
            except ValueError as e:
                return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}

        authorScoreMap = {}
        countryScoreMap = {}
        organizationScoreMap ={}
        for Info in combinedLines:
            name = str(Info[int(combinedDict.get("author.First Name"))] + " " + Info[int(combinedDict.get("author.Last Name"))])
            try:
                score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
            except ValueError as e:
                return {"error": "Oops! Value Error occurred. There seems to be an error related to the information in review - overall evaluation score"}

            country = str(Info[int(combinedDict.get("author.Country"))])
            affiliation = str(Info[int(combinedDict.get("author.Organization"))])

            if name not in authorScoreMap:
                authorScoreMap[name] = [score]
            else:
                authorScoreMap[name].append(score)

            if country not in countryScoreMap:
                countryScoreMap[country] = [score]
            else:
                countryScoreMap[country].append(score)

            if affiliation not in organizationScoreMap:
                organizationScoreMap[affiliation] = [score]
            else:
                organizationScoreMap[affiliation].append(score)

        #getting average of each author
        for key,value in authorScoreMap.iteritems():
            authorScoreMap[key] = sum(value)/float(len(value))

        sorted(authorScoreMap, key=authorScoreMap.get, reverse=True)
        authorScoreList = sorted(authorScoreMap.iteritems(), key=lambda (k,v): (v,k), reverse=True)

        authorScoreMapTop10 = Counter(authorScoreMap)
        authorScoreMapTop10 = authorScoreMapTop10.most_common(10)

        #getting average of each country
        for key,value in countryScoreMap.iteritems():
            countryScoreMap[key] = sum(value)/float(len(value))

        sorted(countryScoreMap, key=countryScoreMap.get, reverse=True)
        countryScoreMapTop10 = Counter(countryScoreMap)
        countryScoreMapTop10 = countryScoreMapTop10.most_common(10)

        #getting average of each organization
        for key,value in organizationScoreMap.iteritems():
            organizationScoreMap[key] = sum(value)/float(len(value))

        sorted(organizationScoreMap, key=organizationScoreMap.get, reverse=True)
        organizationScoreMapTop10 = Counter(organizationScoreMap)
        organizationScoreMapTop10 = organizationScoreMapTop10.most_common(10)

        distinctNumScores = []

        endIndex = len(authorScoreList)
        for idx in range(len(authorScoreList)):
            if (authorScoreList[idx][1] not in distinctNumScores):
                distinctNumScores.append(authorScoreList[idx][1])
            if (len(distinctNumScores) > 10):
                #top 10
                endIndex = idx-1
                break
        authorScoreList = authorScoreList[:endIndex]

        infoAndScore = zip(reviewScoreArr, nameArr, affiliationArr, countryArr)[:endIndex]
        infoAndScore.sort(reverse=True)

        parsedResult['topAuthorsAR'] =  {'authors': [ele[0] for ele in authorScoreList],
        'score': [ele[1] for ele in authorScoreList]}       #topAuthorsScore
        parsedResult['affiliationDistributionAR'] = {'organization': [ele[2] for ele in infoAndScore],
        'score': [ele[0] for ele in infoAndScore]}
        parsedResult['countryDistributionAR'] = {'country': [ele[3] for ele in infoAndScore],                
        'score': [ele[0] for ele in infoAndScore], 'author': [ele[1] for ele in infoAndScore]} 
        parsedResult['topCountriesAR'] = {'countries': [ele[0] for ele in countryScoreMapTop10],
        'score': [round(ele[1],3) for ele in countryScoreMapTop10]}
        parsedResult['topAffiliationsAR'] = {'organization': [ele[0] for ele in organizationScoreMapTop10],
        'score': [round(ele[1],3) for ele in organizationScoreMapTop10]}

        return parsedResult

    def getAuthorSubmissionInfo(self, index):
        authorDict = self.getAuthorOrder(index)
        submissionDict = self.getSubmissionOrder(index)
        combinedDict = self.csvDataList[index].order

        inputFile1 = self.csvDataList[index].csvFiles.get('author')
        inputFile2 = self.csvDataList[index].csvFiles.get('submission')

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get("author.HasHeader")))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get("submission.HasHeader")))

        combinedLines = combineLinesOnKey(lines1, lines2, "author.Submission #", "submission.Submission #", authorDict, submissionDict)
 
        acceptedCountriesList = []
        for ele in combinedLines:
            if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept':
                acceptedCountriesList.append(ele[int(combinedDict.get("author.Country"))])
        # topCountriesList = dict(Counter(acceptedCountriesList).most_common(10))
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
 
        decisionBasedOnTopAffiliations = []
        tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in combinedLines]).keys())
        for track in tracks:
            acceptedSubmissionsByAffiliationAndTrack = []
            for ele in combinedLines:
                if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept' and str(ele[int(combinedDict.get("submission.Track Name"))]) == track:
                    acceptedSubmissionsByAffiliationAndTrack.append(ele[int(combinedDict.get("author.Organization"))])
            # topAffiliationsList = dict(Counter(acceptedSubmissionsByAffiliationAndTrack).most_common(10))
            topAffiliationsList = dict(Counter(acceptedSubmissionsByAffiliationAndTrack))
            topAffiliationsList = sorted(topAffiliationsList.iteritems(), key=lambda (k,v): (v,k), reverse=True)
            
            topAffiliationDataForTrack = []

            distinctNumDecisions = []
            endIndex = len(topAffiliationsList)
            for i in range(len(topAffiliationsList)):
                if (topAffiliationsList[i] not in distinctNumDecisions):
                    distinctNumDecisions.append(topAffiliationsList[i])
                if (len(distinctNumDecisions) > 10):
                    #top 10
                    endIndex = i-1
                    break
            topAffiliationsList = topAffiliationsList[:endIndex]
            topAffiliationDataForTrack.append([key for key, value in topAffiliationsList])
            topAffiliationDataForTrack.append([value for key, value in topAffiliationsList])
            decisionBasedOnTopAffiliations.append(topAffiliationDataForTrack)
            

        parsedResult['topCountriesAS'] = {'labels': [key for key, value in topCountriesList], 'data': [value for key, value in topCountriesList]}
        parsedResult['topAffiliationsAS'] = {'labels':tracks, 'data': decisionBasedOnTopAffiliations}

        # ######## PRINTING LIST OF HEADER-COLUMN VALUES ########
        # for key, value in combinedDict.items():
        #     print key
        #     print [str(ele[value]) for ele in combinedLines]
        #     print ("====================================")
        # print ("====================================")
        # print parsedResult['topCountriesAS']
        # print "==="
        # print parsedResult['topAffiliationsAS']
        # print ("====================================")

        return parsedResult

    def getReviewSubmissionInfo(self, index):
        reviewDict = self.getReviewOrder(index)
        submissionDict = self.getSubmissionOrder(index)
        combinedDict = self.csvDataList[index].order
        inputFile1 = self.csvDataList[index].csvFiles.get('review')
        inputFile2 = self.csvDataList[index].csvFiles.get('submission')

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get("review.HasHeader")))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get("submission.HasHeader")))
        combinedLines = combineLinesOnKey(lines1, lines2, "review.Submission #", "submission.Submission #", reviewDict, submissionDict)

        tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in combinedLines]).keys())
        expertiseByTrack = dict()
        for track in tracks:
            dataListForCurrentTrack = []
            for line in combinedLines:
                if (line[int(combinedDict.get("submission.Track Name"))] == track):
                    dataListForCurrentTrack.append(line[int(combinedDict.get("review.Field #"))])
            expertiseByTrack[track] = dict(Counter(dataListForCurrentTrack))

        meanScoreByTrack = dict()
        for track in tracks:
            scoreListForCurrentTrack = []
            for line in combinedLines:
                if (line[int(combinedDict.get("submission.Track Name"))] == track):
                    scoreListForCurrentTrack.append(line[int(combinedDict.get("review.Overall Evaluation Score"))])
            meanScoreByTrack[track] = sum([int(ele) for ele in scoreListForCurrentTrack])/len(scoreListForCurrentTrack)

        parsedResult['expertiseSR'] = {'labels': tracks, 'data': list(expertiseByTrack.values())}
        parsedResult['averageScoreSR'] = {'labels': tracks, 'data': list(meanScoreByTrack.values())}

        # ######## PRINTING LIST OF HEADER-COLUMN VALUES ########
        # for key, value in combinedDict.items():
        #     print key
        #     print [str(ele[value]) for ele in combinedLines if key == "review.Overall Evaluation Score" or key == "submission.Track Name"]
        #     print ("====================================")
        # print ("====================================")
        # print parsedResult['expertiseSR']
        # print parsedResult['averageScoreSR']
        # print ("====================================")

        return parsedResult