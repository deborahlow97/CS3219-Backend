from CsvData import CsvData

import csv
import codecs
from collections import Counter

from polls.utils import parseCSVFile, parseCSVFileInverted, testCSVFileFormatMatching, isNumber, parseSubmissionTime

'''
Represents a builder class to build csv data from an uploaded csv file
'''
class CsvDataBuilder:
    def __init__(self):
        self.csvDataList = []
        self.size = 0

    def addCsvData(self, infoType, dataDictionary, inputFile):
        csvData = CsvData(infoType, dataDictionary, inputFile)
        self.csvDataList.append(csvData)
        self.size += 1

    def setOrder(self, index):
        order = self.getOrder(index)
        self.csvDataList[index].setOrder(order)
        
    def getOrder(self, index):
        order = []
        type = self.csvDataList[index].infoType
        if type == "author":
            order = self.getAuthorOrder(index)
        elif type == "review":
            order = self.getReviewOrder(index)
        elif type == "submission":
            order = self.getSubmissionOrder(index)
        elif type == "author.review":
            #TODO: remove placeholder code and add implementation
            order = self.getAuthorOrder(index)
            print ("author + review")
        elif type == "author.submission":
            order = self.getAuthorOrder(index)
            print ("author + submission")
        elif type == "review.submission":
            order = self.getAuthorOrder(index)
            print ("submission + review")
        elif type == "author.review.submission":
            order = self.getAuthorOrder(index)
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
        if type == "author":
            info = self.getAuthorInfo(index)
        elif type == "review":
            info = self.getReviewInfo(index)
            print info
        elif type == "submission":
            info = self.getSubmissionInfo(index)
        elif type == "author.review":
            #TODO: remove placeholder code and add implementation
            info = self.getAuthorInfo(index)
            print ("author + review")
        elif type == "author.submission":
            info = self.getAuthorInfo(index)
            print ("author + submission")
        elif type == "review.submission":
            info = self.getAuthorInfo(index)
            print ("submission + review")
        elif type == "author.review.submission":
            info = self.getAuthorInfo(index)
            print ("author + review + submission")            
        else:
            print ("ERROR: No such info")
        print info
        return info
            
    def formatRowContent(self):
        rowContent = {}

        infoType = []
        for i in range(self.size):
            csvData = self.csvDataList[i]
            print csvData.infoType
            infoType.append(csvData.infoType)

        rowContent['infoType'] = infoType

        # print "="
        # print rowContent
        # print "="

        print (self.size)
        infoData = ""
        for i in range(self.size - 1):
            print i
            csvData = self.csvDataList[i]
            infoData += csvData.info + ", "
        infoData += repr(self.csvDataList[-1].info)
        
        rowContent['infoData'] = infoData

        # print ("===")
        # print(self.csvDataList[-1].info)
        # print ("===")

        return rowContent

    def getAuthorOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        authorArray = []

        for key, value in dataDictionary.iteritems():
            if "author." in key:
                authorArray.insert(int(value), str(key))

        return authorArray

    def getReviewOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        reviewArray = []

        for key, value in dataDictionary.iteritems():
            if "review." in key:
                reviewArray.insert(int(value), str(key))

        return reviewArray

    def getSubmissionOrder(self, index):
        dataDictionary = self.csvDataList[index].data
        submissionArray = []

        for key, value in dataDictionary.iteritems():
            if "submission." in key:
                submissionArray.insert(int(value), str(key))

        return submissionArray

    '''
    ==================================== GET INFO METHODS =====================================
    '''
    def getAuthorInfo(self, index):
        authorArray = self.csvDataList[index].order
        inputFile = self.csvDataList[index].csvFile

        """
        author.csv: header row, author names with affiliations, countries, emails
        data format:
        submission ID | f name | s name | email | country | affiliation | page | person ID | corresponding?
        """

        parsedResult = {}
        #Case 1: Header given in CSV File - array is empty
        if not authorArray:
            lines = parseCSVFile(inputFile)[1:]
        #Case 2: Header not given in CSV file 
        else:
            lines = parseCSVFile(inputFile)
        
        lines = [ele for ele in lines if ele]

        #invertedLines = parseCSVFileInverted(lines)

        authorList = []
        # for x in lines:
        # 	print(x)
        print len(lines)

        for authorInfo in lines:
            #authorInfo = line.replace("\"", "").split(",")
            authorList.append(
                {'name': str(authorInfo[int(authorArray.index("author.First Name"))]) + " " + str(authorInfo[int(authorArray.index("author.Last Name"))]),
                'country': str(authorInfo[int(authorArray.index("author.Country"))]),
                'affiliation': str(authorInfo[int(authorArray.index("author.Organization"))])})
        
        # if not authorArray:
        authors = [ele['name'] for ele in authorList if ele] # adding in the if ele in case of empty strings; same applies below
        topAuthors = Counter(authors).most_common(10)
        parsedResult['topAuthors'] = {'labels': [ele[0] for ele in topAuthors], 'data': [ele[1] for ele in topAuthors]}

        # for x in parsedResult:
        # 	for y in x['topAuthors']:
        # 		print str(y['labels']) + " aaa " + str(y['data'])

        countries = [ele['country'] for ele in authorList if ele]
        topCountries = Counter(countries).most_common(10)
        parsedResult['topCountries'] = {'labels': [ele[0] for ele in topCountries], 'data': [ele[1] for ele in topCountries]}

        affiliations = [ele['affiliation'] for ele in authorList if ele]
        topAffiliations = Counter(affiliations).most_common(10)
        parsedResult['topAffiliations'] = {'labels': [ele[0] for ele in topAffiliations], 'data': [ele[1] for ele in topAffiliations]}

        return parsedResult
        # return {'infoType': 'author', 'infoData': parsedResult}

    def getReviewInfo(self, index):
        #TODO: STILL BUGGY
        reviewArray = self.csvDataList[index].order
        inputFile = self.csvDataList[index].csvFile
        print ("INSIDE REVIEW INFO")
        print reviewArray

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
        evaluation = [str(line[int(reviewArray.index("review.Overall Evaluation Score (ignore)"))]).replace("\r", "") for line in lines]
        submissionIDs = set([str(line[int(reviewArray.index("review.Submission #"))]) for line in lines])

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
        print "adfsgbhtf"

        for submissionID in submissionIDs:
            reviews = [str(line[int(reviewArray.index("review.Overall Evaluation Score (ignore)"))]).replace("\r", "") for line in lines if str(line[int(reviewArray.index("review.Submission #"))]) == submissionID]
            print (reviews)
            # print reviews
            confidences = [float(review.split("\n")[1].split(": ")[1]) for review in reviews]
            print (confidenceList)
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
        print "hello"

        parsedResult['IDReviewMap'] = submissionIDReviewMap
        parsedResult['scoreList'] = scoreList
        parsedResult['meanScore'] = sum(scoreList) / len(scoreList)
        parsedResult['meanRecommend'] = sum(recommendList) / len(recommendList)
        parsedResult['meanConfidence'] = sum(confidenceList) / len(confidenceList)
        parsedResult['recommendList'] = recommendList
        parsedResult['scoreDistribution'] = {'labels': scoreDistributionLabels, 'counts': scoreDistributionCounts}
        parsedResult['recommendDistribution'] = {'labels': recommendDistributionLabels, 'counts': recommendDistributionCounts}

        print ("-----------------")
        print parsedResult
        print ("-----------------")
        return parsedResult
        # return {'infoType': 'review', 'infoData': parsedResult}
        
    def getSubmissionInfo(self, index):
        submissionArray = self.csvDataList[index].order
        inputFile = self.csvDataList[index].csvFile

        """
        submission.csv
        data format: 
        submission ID | track ID | track name | title | authors | submit time | last update time | form fields | keywords | decision | notified | reviews sent | abstract
        File has header
        """

        parsedResult = {}
        #Case 1: Header given in CSV File - array is empty
        if not submissionArray:
            lines = parseCSVFile(inputFile)[1:]
        #Case 2: Header not given in CSV file 
        else:
            lines = parseCSVFile(inputFile)

        #change list of list to -> remove empty rows
        lines = [ele for ele in lines if ele]

        """
            lines = []
            for ele in lines:
                if ele
                    lines.append(ele)
        """
        acceptedSubmission = [line for line in lines if str(line[int(submissionArray.index("submission.Decision"))]) == 'accept']
        rejectedSubmission = [line for line in lines if str(line[int(submissionArray.index("submission.Decision"))]) == 'reject']

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
        paperGroupsByTrack = {track : [line for line in lines if str(line[int(submissionArray.index("submission.Track Name"))]) == track] for track in tracks}
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

        return parsedResult
        # return {'infoType': 'submission', 'infoData': parsedResult}