from CsvData import CsvData

import csv
import codecs
from collections import Counter

from polls.utils import parseCSVFile, parseCSVFileInverted, testCSVFileFormatMatching, isNumber, parseSubmissionTime

'''
Represents data from an uploaded review.csv file
'''
class Review(CsvData):
    def __init__(self, dataDictionary, inputFile):
        CsvData.__init__(self, dataDictionary, inputFile)

    def getOrder(self):
        dataDictionary = self.data
        reviewArray = []

        #['ReviewID', 'SubmissionIDR', 'ReviewAssignmentID', 'ReviewerName', 'FieldID'
        # 'Comments', 'OverallEvalScoreExtra', 'OverallEvalScore', 'SubreviewerInfo1'
        # 'SubreviewerInfo2','SubreviewerInfo3','SubreviewerInfo4', 'Date', 'Time'
        # 'RecommendationForBestPaper' ]
        
        reviewArray.insert(int(dataDictionary.get('review.Overall Evaluation Score (ignore)')), "OverallEvalScoreExtra")
        reviewArray.insert(int(dataDictionary.get('review.Field #')), "FieldID")
        reviewArray.insert(int(dataDictionary.get('review.Subreviewer Info 4 (ignore)')), "SubreviewerInfo4")
        reviewArray.insert(int(dataDictionary.get('review.Date')), "Date")
        reviewArray.insert(int(dataDictionary.get('review.Subreviewer Info 2 (ignore)')), "SubreviewerInfo2")
        reviewArray.insert(int(dataDictionary.get('review.Overall Evaluation Score')), "OverallEvalScore")
        reviewArray.insert(int(dataDictionary.get('review.Submission #')), "SubmissionIDR")
        reviewArray.insert(int(dataDictionary.get('review.Recommendation for Best Paper')), "RecommendationForBestPaper")
        reviewArray.insert(int(dataDictionary.get('review.Review Assignment #')), "ReviewAssignmentID")
        reviewArray.insert(int(dataDictionary.get('review.Subreviewer Info 3 (ignore)')), "SubreviewerInfo3")
        reviewArray.insert(int(dataDictionary.get('review.Time')), "Time")
        reviewArray.insert(int(dataDictionary.get('review.Comments')), "Comments")
        reviewArray.insert(int(dataDictionary.get('review.Reviewer Name')), "ReviewerName")
        reviewArray.insert(int(dataDictionary.get('review.Review #')), "ReviewID")
        reviewArray.insert(int(dataDictionary.get('review.Subreviewer Info 1 (ignore)')), "SubreviewerInfo1")
        
        # for x in reviewArray:
        # 	print (x)

        self.array = reviewArray

        return reviewArray

    def getInfo(self):
        reviewArray = self.array
        inputFile = self.csvFile

        """
        review.csv
        data format: 
        review ID | paper ID? | reviewer ID | reviewer name | unknown | text | scores | overall score | unknown | unknown | unknown | unknown | date | time | recommend?
        File has NO header

        score calculation principles:
        Weighted Average of the scores, using reviewer's confidence as the weights

        recommended principles:
        Yes: 1; No: 0; weighted average of the 1 and 0's, also using reviewer's confidence as the weights
        """

        parsedResult = {}
        #Case 1: Header given in CSV File - array is empty
        if not reviewArray:
            lines = parseCSVFile(inputFile)[1:]
        #Case 2: Header not given in CSV file 
        else:
            lines = parseCSVFile(inputFile)

        lines = [ele for ele in lines if ele]
        evaluation = [str(line[6]).replace("\r", "") for line in lines]
        submissionIDs = set([str(line[1]) for line in lines])

        scoreList = []
        recommendList = []
        confidenceList = []

        submissionIDReviewMap = {}

        # Idea: from -3 to 3 (min to max scores possible), every 0.25 will be a gap
        scoreDistributionCounts = [0] * int((3 + 3) / 0.25)
        recommendDistributionCounts = [0] * int((1 - 0) / 0.1)

        scoreDistributionLabels = [" ~ "] * len(scoreDistributionCounts)
        recommendDistributionLabels = [" ~ "] * len(recommendDistributionCounts)

        for index, col in enumerate(scoreDistributionCounts):
            scoreDistributionLabels[index] = str(-3 + 0.25 * index) + " ~ " + str(-3 + 0.25 * index + 0.25)

        for index, col in enumerate(recommendDistributionCounts):
            recommendDistributionLabels[index] = str(0 + 0.1 * index) + " ~ " + str(0 + 0.1 * index + 0.1)

        for submissionID in submissionIDs:
            reviews = [str(line[6]).replace("\r", "") for line in lines if str(line[1]) == submissionID]
            # print reviews
            confidences = [float(review.split("\n")[1].split(": ")[1]) for review in reviews]
            scores = [float(review.split("\n")[0].split(": ")[1]) for review in reviews]

            confidenceList.append(sum(confidences) / len(confidences))
            # recommends = [1.0 for review in reviews if review.split("\n")[2].split(": ")[1] == "yes" else 0.0]
            try:
                recommends = map(lambda review: 1.0 if review.split("\n")[2].split(": ")[1] == "yes" else 0.0, reviews)
            except:
                recommends = [0.0 for n in range(len(reviews))]
            weightedScore = sum(x * y for x, y in zip(scores, confidences)) / sum(confidences)
            weightedRecommend = sum(x * y for x, y in zip(recommends, confidences)) / sum(confidences)

            scoreColumn = min(int((weightedScore + 3) / 0.25), 23)
            recommendColumn = min(int((weightedRecommend) / 0.1), 9)
            scoreDistributionCounts[scoreColumn] += 1
            recommendDistributionCounts[recommendColumn] += 1
            submissionIDReviewMap[submissionID] = {'score': weightedScore, 'recommend': weightedRecommend}
            scoreList.append(weightedScore)
            recommendList.append(weightedRecommend)


        parsedResult['IDReviewMap'] = submissionIDReviewMap
        parsedResult['scoreList'] = scoreList
        parsedResult['meanScore'] = sum(scoreList) / len(scoreList)
        parsedResult['meanRecommend'] = sum(recommendList) / len(recommendList)
        parsedResult['meanConfidence'] = sum(confidenceList) / len(confidenceList)
        parsedResult['recommendList'] = recommendList
        parsedResult['scoreDistribution'] = {'labels': scoreDistributionLabels, 'counts': scoreDistributionCounts}
        parsedResult['recommendDistribution'] = {'labels': recommendDistributionLabels, 'counts': recommendDistributionCounts}

        return {'infoType': 'review', 'infoData': parsedResult}
