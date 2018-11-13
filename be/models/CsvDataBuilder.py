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
            order = combineOrderDict(self.getAuthorOrder(index), self.getReviewOrder(index))
        elif type == "author.submission":
            order = combineOrderDict(self.getAuthorOrder(index), self.getSubmissionOrder(index))
        elif type == "review.submission":
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
        elif type == "author.submission":
            info = self.getAuthorSubmissionInfo(index)
        elif type == "review.submission":
            info = self.getReviewSubmissionInfo(index)
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
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthors(lines, authorDict))
        parsedResult.update(calculationUtil.getTopCountries(lines, authorDict))
        parsedResult.update(calculationUtil.getTopAffiliations(lines, authorDict))
        return parsedResult

    def getReviewInfo(self, index, dict = None):
        if (dict is None):
            reviewDict = self.csvDataList[index].order
        else:
            reviewDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('review')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(reviewDict.get("review.HasHeader")))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getReviewTimeSeries(lines, reviewDict))
        parsedResult.update(calculationUtil.getScoreDistribution(lines, reviewDict))
        parsedResult.update(calculationUtil.getMeanEvScoreByExpertiseLevel(lines, reviewDict))

        return parsedResult
        
    def getSubmissionInfo(self, index, dict = None):
        if (dict is None):
            submissionDict = self.csvDataList[index].order
        else:
            submissionDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('submission')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(submissionDict.get("submission.HasHeader")))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthorsByTrackAndAcceptanceRate(lines, submissionDict))
        parsedResult.update(calculationUtil.getWordCloudByTrack(lines, submissionDict))
        parsedResult.update(calculationUtil.getSubmissionTimeSeries(lines, submissionDict))
        parsedResult.update(calculationUtil.getAcceptanceRateByTrack(lines, submissionDict))
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
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthorsInfoAR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopCountriesAR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopAffiliationsAR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopCountriesAR(combinedLines, combinedDict))

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
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopCountriesAS(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopAffiliationsAS(combinedLines, combinedDict))
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
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getExpertiseSR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getAverageScoreSR(combinedLines, combinedDict))
        return parsedResult