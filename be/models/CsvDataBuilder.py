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
    def __init__(self, csvData):
        self.csvData = csvData

    # def addCsvData(self, infoType, dataDictionary, inputFiles):
    #     csvData = CsvData(infoType, dataDictionary, inputFiles)
    #     self.csvDataList.append(csvData)        
        
    def setOrder(self):
        order = self.getOrder()
        self.csvData.setOrder(order)

    def getOrder(self):
        order = {}
        type = self.csvData.infoType
        if type == "author.csv":
            order = self.getAuthorOrder()
        elif type == "review.csv":
            order = self.getReviewOrder()
        elif type == "submission.csv":
            order = self.getSubmissionOrder()
        elif type == "author.review":
            order = combineOrderDict(self.getAuthorOrder(), self.getReviewOrder())
        elif type == "author.submission":
            order = combineOrderDict(self.getAuthorOrder(), self.getSubmissionOrder())
        elif type == "review.submission":
            order = combineOrderDict(self.getReviewOrder(), self.getSubmissionOrder())
        elif type == "author.review.submission":
            print ("author + review + submission")
        else:
            print ("ERROR: No such type")
        return order
        
    def setInfo(self):
        info = self.getInfo()
        self.csvData.setInfo(info)

    def getInfo(self):
        info = {}
        type = self.csvData.infoType
        if type == "author.csv":
            info = self.getAuthorInfo()
        elif type == "review.csv":
            info = self.getReviewInfo()
        elif type == "submission.csv":
            info = self.getSubmissionInfo()
        elif type == "author.review":
            info = self.getAuthorReviewInfo()
        elif type == "author.submission":
            info = self.getAuthorSubmissionInfo()
        elif type == "review.submission":
            info = self.getReviewSubmissionInfo()
        elif type == "author.review.submission":
            info = {}
            print ("author + review + submission")            
        else:
            print ("ERROR: No such info")
        return info

    def getAuthorOrder(self):
        dataDictionary = self.csvData.data
        authorDict = {}

        for key, value in dataDictionary.iteritems():
            if "author.HasHeader" in key:
                authorDict.update({str(key): bool(value)})
            elif "author." in key:
                authorDict.update({str(key): int(value)})
                
        return authorDict

    def getReviewOrder(self):
        dataDictionary = self.csvData.data
        reviewDict = {}

        for key, value in dataDictionary.iteritems():
            if "review.HasHeader" in key:
                reviewDict.update({str(key): bool(value)})
            elif "review." in key:
                reviewDict.update({str(key): int(value)})

        return reviewDict

    def getSubmissionOrder(self):
        dataDictionary = self.csvData.data
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
    def getAuthorInfo(self):
        authorDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get('author')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(authorDict.get("author.HasHeader")))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthors(lines, authorDict))
        parsedResult.update(calculationUtil.getTopCountries(lines, authorDict))
        parsedResult.update(calculationUtil.getTopAffiliations(lines, authorDict))
        return parsedResult

    def getReviewInfo(self):
        reviewDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get('review')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(reviewDict.get("review.HasHeader")))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getReviewTimeSeries(lines, reviewDict))
        parsedResult.update(calculationUtil.getScoreDistribution(lines, reviewDict))
        parsedResult.update(calculationUtil.getMeanEvScoreByExpertiseLevel(lines, reviewDict))

        return parsedResult
        
    def getSubmissionInfo(self):
        submissionDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get('submission')

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(submissionDict.get("submission.HasHeader")))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthorsByTrackAndAcceptanceRate(lines, submissionDict))
        parsedResult.update(calculationUtil.getWordCloudByTrack(lines, submissionDict))
        parsedResult.update(calculationUtil.getSubmissionTimeSeries(lines, submissionDict))
        parsedResult.update(calculationUtil.getAcceptanceRateByTrack(lines, submissionDict))
        return parsedResult

    def getAuthorReviewInfo(self):
        authorDict = self.getAuthorOrder()
        reviewDict = self.getReviewOrder()
        combinedDict = self.csvData.order
        inputFile1 = self.csvData.csvFiles.get('author')
        inputFile2 = self.csvData.csvFiles.get('review')

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

    def getAuthorSubmissionInfo(self):
        authorDict = self.getAuthorOrder()
        submissionDict = self.getSubmissionOrder()
        combinedDict = self.csvData.order

        inputFile1 = self.csvData.csvFiles.get('author')
        inputFile2 = self.csvData.csvFiles.get('submission')

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get("author.HasHeader")))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get("submission.HasHeader")))

        combinedLines = combineLinesOnKey(lines1, lines2, "author.Submission #", "submission.Submission #", authorDict, submissionDict)
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopCountriesAS(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopAffiliationsAS(combinedLines, combinedDict))
        return parsedResult

    def getReviewSubmissionInfo(self):
        reviewDict = self.getReviewOrder()
        submissionDict = self.getSubmissionOrder()
        combinedDict = self.csvData.order
        inputFile1 = self.csvData.csvFiles.get('review')
        inputFile2 = self.csvData.csvFiles.get('submission')

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get("review.HasHeader")))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get("submission.HasHeader")))
        combinedLines = combineLinesOnKey(lines1, lines2, "review.Submission #", "submission.Submission #", reviewDict, submissionDict)
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getExpertiseSR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getAverageScoreSR(combinedLines, combinedDict))
        return parsedResult