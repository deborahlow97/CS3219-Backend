from CsvData import CsvData

import csv
import codecs
import re
from be.CalculationUtil import *
from CsvExceptions import *
from polls.Constants import *
from collections import Counter
from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, isNumber, parseSubmissionTime, appendHasErrorField

'''
Represents a builder class to build csv data from an uploaded csv file
'''
class CsvDataBuilder:
    def __init__(self, csvData):
        self.csvData = csvData

    def setOrder(self):
        order = self.getOrder()
        self.csvData.setOrder(order)

    def getOrder(self):
        order = {}
        type = self.csvData.infoType
        if type == AUTHOR_CSV:
            order = self.getAuthorOrder()
        elif type == REVIEW_CSV:
            order = self.getReviewOrder()
        elif type == SUBMISSION_CSV:
            order = self.getSubmissionOrder()
        elif type == AUTHOR_REVIEW:
            order = combineOrderDict(self.getAuthorOrder(), self.getReviewOrder())
        elif type == AUTHOR_SUBMISSION:
            order = combineOrderDict(self.getAuthorOrder(), self.getSubmissionOrder())
        elif type == REVIEW_SUBMISSION:
            order = combineOrderDict(self.getReviewOrder(), self.getSubmissionOrder())
        elif type == AUTHOR_REVIEW_SUBMISSION:
            print ""
        else:
            print ("ERROR: No such type")
        return order
        
    def setInfo(self):
        info = self.getInfo()
        self.csvData.setInfo(info)

    def getInfo(self):
        info = {}
        type = self.csvData.infoType
        if type == AUTHOR_CSV:
            info = self.getAuthorInfo()
        elif type == REVIEW_CSV:
            info = self.getReviewInfo()
        elif type == SUBMISSION_CSV:
            info = self.getSubmissionInfo()
        elif type == AUTHOR_REVIEW:
            info = self.getAuthorReviewInfo()
        elif type == AUTHOR_SUBMISSION:
            info = self.getAuthorSubmissionInfo()
        elif type == REVIEW_SUBMISSION:
            info = self.getReviewSubmissionInfo()
        elif type == AUTHOR_REVIEW_SUBMISSION:
            info = {}
            print ("author + review + submission")            
        else:
            print ("ERROR: No such info")
        return info

    def getAuthorOrder(self):
        dataDictionary = self.csvData.data
        authorDict = {}

        for key, value in dataDictionary.iteritems():
            if AUTHOR_HAS_HEADER in key:
                authorDict.update({str(key): bool(value)})
            elif "author." in key:
                authorDict.update({str(key): int(value)})
                
        return authorDict

    def getReviewOrder(self):
        dataDictionary = self.csvData.data
        reviewDict = {}

        for key, value in dataDictionary.iteritems():
            if REVIEW_HAS_HEADER in key:
                reviewDict.update({str(key): bool(value)})
            elif "review." in key:
                reviewDict.update({str(key): int(value)})

        return reviewDict

    def getSubmissionOrder(self):
        dataDictionary = self.csvData.data
        submissionDict = {}

        for key, value in dataDictionary.iteritems():
            if SUBMISSION_HAS_HEADER in key:
                submissionDict.update({str(key): bool(value)})
            elif "submission." in key:

                submissionDict.update({str(key): int(value)})

        return submissionDict

    '''
    ==================================== GET INFO METHODS =====================================
    '''
    def getAuthorInfo(self):
        authorDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get(AUTHOR)

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(authorDict.get(AUTHOR_HAS_HEADER)))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopAuthors(lines, authorDict))
        parsedResult.update(calculationUtil.getTopCountries(lines, authorDict))
        parsedResult.update(calculationUtil.getTopAffiliations(lines, authorDict))
        return parsedResult

    def getReviewInfo(self):
        reviewDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get(REVIEW)

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(reviewDict.get(REVIEW_HAS_HEADER)))
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getReviewTimeSeries(lines, reviewDict))
        parsedResult.update(calculationUtil.getScoreDistribution(lines, reviewDict))
        parsedResult.update(calculationUtil.getMeanEvScoreByExpertiseLevel(lines, reviewDict))

        return parsedResult
        
    def getSubmissionInfo(self):
        submissionDict = self.csvData.order
        inputFile = self.csvData.csvFiles.get(SUBMISSION)

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(submissionDict.get(SUBMISSION_HAS_HEADER)))
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
        inputFile1 = self.csvData.csvFiles.get(AUTHOR)
        inputFile2 = self.csvData.csvFiles.get(REVIEW)

        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get(AUTHOR_HAS_HEADER)))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get(REVIEW_HAS_HEADER)))
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

        inputFile1 = self.csvData.csvFiles.get(AUTHOR)
        inputFile2 = self.csvData.csvFiles.get(SUBMISSION)

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get(AUTHOR_HAS_HEADER)))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get(SUBMISSION_HAS_HEADER)))

        combinedLines = combineLinesOnKey(lines1, lines2, "author.Submission #", "submission.Submission #", authorDict, submissionDict)
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getTopCountriesAS(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getTopAffiliationsAS(combinedLines, combinedDict))
        return parsedResult

    def getReviewSubmissionInfo(self):
        reviewDict = self.getReviewOrder()
        submissionDict = self.getSubmissionOrder()
        combinedDict = self.csvData.order
        inputFile1 = self.csvData.csvFiles.get(REVIEW)
        inputFile2 = self.csvData.csvFiles.get(SUBMISSION)

        parsedResult = {}
        lines1 = getLinesFromInputFile(inputFile1, bool(combinedDict.get(REVIEW_HAS_HEADER)))
        lines2 = getLinesFromInputFile(inputFile2, bool(combinedDict.get(SUBMISSION_HAS_HEADER)))
        combinedLines = combineLinesOnKey(lines1, lines2, "review.Submission #", "submission.Submission #", reviewDict, submissionDict)
        calculationUtil = CalculationUtil()
        parsedResult.update(calculationUtil.getExpertiseSR(combinedLines, combinedDict))
        parsedResult.update(calculationUtil.getAverageScoreSR(combinedLines, combinedDict))
        return parsedResult