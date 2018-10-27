from CsvData import CsvData

import csv
import codecs
from collections import Counter

from polls.utils import combineOrderDict, getLinesFromInputFile, combineLinesOnKey, parseCSVFile, parseCSVFileInverted, isNumber, parseSubmissionTime

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
        order = []
        type = self.csvDataList[index].infoType
        if type == "author":
            order = self.getAuthorOrder(index)
        elif type == "review":
            order = self.getReviewOrder(index)
        elif type == "submission":
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
        if type == "author":
            info = self.getAuthorInfo(index)
        elif type == "review":
            info = self.getReviewInfo(index)
        elif type == "submission":
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
            print csvData.infoType
            infoType.append(csvData.infoType)
            infoData.update(csvData.info)

        rowContent['infoType'] = infoType
        rowContent['infoData'] = infoData

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

        """
        author.csv: header row, author names with affiliations, countries, emails
        data format:
        submission ID | f name | s name | email | country | affiliation | page | person ID | corresponding?
        """

        parsedResult = {}

        lines = getLinesFromInputFile(inputFile, bool(authorDict.get("author.HasHeader")))
        authorList = []
        print len(lines)

        for authorInfo in lines:
            #authorInfo = line.replace("\"", "").split(",")
            authorList.append(
                {'name': str(authorInfo[int(authorDict.get("author.First Name"))]) + " " + str(authorInfo[int(authorDict.get("author.Last Name"))]),
                'country': str(authorInfo[int(authorDict.get("author.Country"))]),
                'affiliation': str(authorInfo[int(authorDict.get("author.Organization"))])})

        authors = [ele['name'] for ele in authorList if ele] # adding in the if ele in case of empty strings; same applies below
        topAuthors = Counter(authors).most_common(10)
        parsedResult['topAuthors'] = {'labels': [ele[0] for ele in topAuthors], 'data': [ele[1] for ele in topAuthors]}

        # for x in parsedResult:
        # 	for y in x['topAuthors']:
        # 		print str(y['labels']) + " aaa " + str(y['data'])

        countries = [ele['country'] for ele in authorList if ele]
        topCountries = Counter(countries).most_common(10)
        parsedResult['topCountries'] = {'labels': [ele[0] for ele in topCountries], 'data': [ele[1] for ele in topCountries]}
        #print (parsedResult['topCountries'])
        affiliations = [ele['affiliation'] for ele in authorList if ele]
        topAffiliations = Counter(affiliations).most_common(10)
        parsedResult['topAffiliations'] = {'labels': [ele[0] for ele in topAffiliations], 'data': [ele[1] for ele in topAffiliations]}
        #print (parsedResult['topAffiliations'])
        return parsedResult

    def getReviewInfo(self, index, dict = None):
        if (dict is None):
            reviewDict = self.csvDataList[index].order
        else:
            reviewDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('review')
        # print reviewDict

        """
        review.csv

        score calculation principles:
        Weighted Average of the scores, using reviewer's confidence as the weights

        recommended principles:
        Yes: 1; No: 0; weighted average of the 1 and 0's, also using reviewer's confidence as the weights
        """

        parsedResult = {}

        lines = getLinesFromInputFile(inputFile, bool(reviewDict.get("review.HasHeader")))

        evaluation = [str(line[int(reviewDict.get("review.Overall Evaluation Score (ignore)"))]).replace("\r", "") for line in lines]
        submissionIDs = set([str(line[int(reviewDict.get("review.Submission #"))]) for line in lines])
        reviewTime = [str(ele[int(reviewDict.get("review.Time"))]) for ele in lines]
        reviewDate = [str(ele[int(reviewDict.get("review.Date"))]) for ele in lines]
        reviewDate = Counter(reviewDate)
        lastReviewStamps = sorted([k for k in reviewDate])
        reviewedNumber = [0 for n in range(len(lastReviewStamps))]
        #lastEditNumber = [0 for n in range(len(lastEditStamps))]
        reviewTimeSeries = []
        for index, lastReviewStamps in enumerate(lastReviewStamps):
            if index == 0:
                reviewedNumber[index] = reviewDate[lastReviewStamps]
            else:
                reviewedNumber[index] = reviewDate[lastReviewStamps] + reviewedNumber[index - 1]

            reviewTimeSeries.append({'x': lastReviewStamps, 'y': reviewedNumber[index]})

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
            reviews = [str(line[int(reviewDict.get("review.Overall Evaluation Score (ignore)"))]).replace("\r", "") for line in lines if str(line[int(reviewDict.get("review.Submission #"))]) == submissionID]
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
        parsedResult['reviewTimeSeries'] = reviewTimeSeries
        return parsedResult
        
    def getSubmissionInfo(self, index, dict = None):
        if (dict is None):
            submissionDict = self.csvDataList[index].order
        else:
            submissionDict = dict
        inputFile = self.csvDataList[index].csvFiles.get('submission')

        """
        submission.csv
        """

        parsedResult = {}
        lines = getLinesFromInputFile(inputFile, bool(submissionDict.get("submission.HasHeader")))

        """
            lines = []
            for ele in lines:
                if ele
                    lines.append(ele)
        """
        acceptedSubmission = [line for line in lines if str(line[int(submissionDict.get("submission.Decision"))]) == 'accept']
        rejectedSubmission = [line for line in lines if str(line[int(submissionDict.get("submission.Decision"))]) == 'reject']

        acceptanceRate = float(len(acceptedSubmission)) / len(lines)

        submissionTimes = [parseSubmissionTime(str(ele[int(submissionDict.get("submission.Time Submitted"))])) for ele in lines]
        lastEditTimes = [parseSubmissionTime(str(ele[int(submissionDict.get("submission.Time Last Updated"))])) for ele in lines]
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

        acceptedKeywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in acceptedSubmission]
        acceptedKeywords = [ele for item in acceptedKeywords for ele in item]
        acceptedKeywordMap = {k : v for k, v in Counter(acceptedKeywords).iteritems()}
        acceptedKeywordList = [[ele[0], ele[1]] for ele in Counter(acceptedKeywords).most_common(20)]

        rejectedKeywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in rejectedSubmission]
        rejectedKeywords = [ele for item in rejectedKeywords for ele in item]
        rejectedKeywordMap = {k : v for k, v in Counter(rejectedKeywords).iteritems()}
        rejectedKeywordList = [[ele[0], ele[1]] for ele in Counter(rejectedKeywords).most_common(20)]

        allKeywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in lines]
        allKeywords = [ele for item in allKeywords for ele in item]
        allKeywordMap = {k : v for k, v in Counter(allKeywords).iteritems()}
        allKeywordList = [[ele[0], ele[1]] for ele in Counter(allKeywords).most_common(20)]

        tracks = set([str(ele[int(submissionDict.get("submission.Track Name"))]) for ele in lines])
        paperGroupsByTrack = {track : [line for line in lines if str(line[int(submissionDict.get("submission.Track Name"))]) == track] for track in tracks}
        keywordsGroupByTrack = {}
        acceptanceRateByTrack = {}
        comparableAcceptanceRate = {}
        topAuthorsByTrack = {}

        # Obtained from the JCDL.org website: past conferences
        comparableAcceptanceRate['year'] = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
        comparableAcceptanceRate['Full Papers'] = [0.29, 0.28, 0.27, 0.29, 0.29, 0.30, 0.29, 0.30]
        comparableAcceptanceRate['Short Papers'] = [0.29, 0.37, 0.31, 0.31, 0.32, 0.50, 0.35, 0.32]
        for track, papers in paperGroupsByTrack.iteritems():
            keywords = [str(ele[int(submissionDict.get("submission.Keyword(s)"))]).lower().replace("\r", "").split("\n") for ele in papers]
            keywords = [ele for item in keywords for ele in item]
            # keywordMap = {k : v for k, v in Counter(keywords).iteritems()}
            keywordMap = [[ele[0], ele[1]] for ele in Counter(keywords).most_common(20)]
            keywordsGroupByTrack[track] = keywordMap

            acceptedPapersPerTrack = [ele for ele in papers if str(ele[int(submissionDict.get("submission.Decision"))]) == 'accept']
            acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)

            acceptedPapersThisTrack = [paper for paper in papers if str(paper[int(submissionDict.get("submission.Decision"))]) == 'accept']
            acceptedAuthorsThisTrack = [str(ele[int(submissionDict.get("submission.Author(s)"))]).replace(" and ", ", ").split(", ") for ele in acceptedPapersThisTrack]
            acceptedAuthorsThisTrack = [ele for item in acceptedAuthorsThisTrack for ele in item]
            topAcceptedAuthorsThisTrack = Counter(acceptedAuthorsThisTrack).most_common(10)
            topAuthorsByTrack[track] = {'names': [ele[0] for ele in topAcceptedAuthorsThisTrack], 'counts': [ele[1] for ele in topAcceptedAuthorsThisTrack]}

            if track == "Full Papers" or track == "Short Papers":
                comparableAcceptanceRate[track].append(float(len(acceptedPapersPerTrack)) / len(papers))

        acceptedAuthors = [str(ele[int(submissionDict.get("submission.Author(s)"))]).replace(" and ", ", ").split(", ") for ele in acceptedSubmission]
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
        # reviewInfo = self.getReviewInfo(index, reviewDict)
        # authorInfo = self.getAuthorInfo(index, authorDict)
        # 1. Top 10 Authors (by mean review score across all the authors submissions) bar : author names (x axis) mean score (y axis) topAuthorsAR.
        # 2. Affiliation distribution of top 10 authors  pie chart:affiliation distribution affiliationDistributionAR
        # 3. Country distribution of top 10 authors  pie chart:country distribution countryDistributionAR
        # 4. Top 10 countries with highest mean scores  bar : countries ( x-axis), mean score(y-axis)  topCountriesAR
        # 5. Top 10 affiliations with highest mean scores bar : affiliations( x-axis), mean score(y-axis)  topAffiliationsAR
        # Top 10 authors that were recommended for best paper  : authors names (x-axis),

        name = []
        reviewScore = []
        affiliation = []
        country = []
        #name and reviewScore MUST be given
        #counter = 1
        for Info in combinedLines:
            
            name.append(str(Info[int(combinedDict.get("author.First Name"))]) + " " + str(Info[int(combinedDict.get("author.Last Name"))]))
            affiliation.append(str(Info[int(combinedDict.get("author.Organization"))]))
            country.append(str(Info[int(combinedDict.get("author.Country"))]))
            reviewScore.append(int(Info[int(combinedDict.get("review.Overall Evaluation Score"))]))
            # try:    
            # except Exception as e:
            #     print "Line is at %d" % (counter)
            # finally:
            #     counter += 1

        infoAndScore = zip(reviewScore, name, affiliation, country)[:10]
        infoAndScore.sort(reverse=True)

        #HashMap with author Name as key
        authorScoreMap = {}
        countryScoreMap = {}
        organizationScoreMap ={}
        for Info in combinedLines:
            name = str(Info[int(combinedDict.get("author.First Name"))] + " " + Info[int(combinedDict.get("author.Last Name"))])
            score = int(Info[int(combinedDict.get("review.Overall Evaluation Score"))])
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

        parsedResult['topAuthorsAR'] =  {'authors': [ele[0] for ele in authorScoreMapTop10],
        'score': [ele[1] for ele in authorScoreMapTop10]}       #topAuthorsScore
        parsedResult['affiliationDistributionAR'] = {'organization': [ele[2] for ele in infoAndScore],
        'score': [ele[0] for ele in infoAndScore]}
        parsedResult['countryDistributionAR'] = {'country': [ele[3] for ele in infoAndScore],                
        'score': [ele[0] for ele in infoAndScore], 'author': [ele[1] for ele in infoAndScore]} 
        parsedResult['topCountriesAR'] = {'countries': [ele[0] for ele in countryScoreMapTop10],
        'score': [ele[1] for ele in countryScoreMapTop10]}
        parsedResult['topAffiliationsAR'] = {'organization': [ele[0] for ele in organizationScoreMapTop10],
        'score': [ele[1] for ele in organizationScoreMapTop10]}

        for x,y in parsedResult.iteritems():
            print ("theresult")
            print (x)
            for key,value in y.iteritems():
                print (key)
                print (value)

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
        # print combinedLines[0]
        # print combinedLines[1]

        acceptedCountriesList = []
        for ele in combinedLines:
            if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept':
                acceptedCountriesList.append(ele[int(combinedDict.get("author.Country"))])
        topCountriesList = dict(Counter(acceptedCountriesList).most_common(10))

        decisionBasedOnTopAffiliations = []
        tracks = list(Counter([str(ele[int(combinedDict.get("submission.Track Name"))]) for ele in combinedLines]).keys())
        for track in tracks:
            acceptedSubmissionsByAffiliationAndTrack = []
            for ele in combinedLines:
                if str(ele[int(combinedDict.get("submission.Decision"))]) == 'accept' and str(ele[int(combinedDict.get("submission.Track Name"))]) == track:
                    acceptedSubmissionsByAffiliationAndTrack.append(ele[int(combinedDict.get("author.Organization"))])
            topAffiliationsList = Counter(acceptedSubmissionsByAffiliationAndTrack).most_common(10)
            decisionBasedOnTopAffiliations.append(dict(topAffiliationsList))

        parsedResult['topCountriesAS'] = {'labels': topCountriesList.keys(), 'data': topCountriesList.values()}
        parsedResult['topAffiliationsAS'] = {'labels':tracks, 'data': decisionBasedOnTopAffiliations}

        # ######## PRINTING LIST OF HEADER-COLUMN VALUES ########
        # for key, value in combinedDict.items():
        #     print key
        #     print [str(ele[value]) for ele in combinedLines]
        #     print ("====================================")
        # print ("====================================")
        print parsedResult['topCountriesAS']
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
        expertiseLevels = ['1', '2', '3', '4', '5']
        expertiseByTrack = dict()
        for track in tracks:
            dataListForCurrentTrack = []
            for line in combinedLines:
                if (line[int(combinedDict.get("submission.Track Name"))] == track):
                    dataListForCurrentTrack.append(line[int(combinedDict.get("review.Field #"))])
            expertiseByTrack[track] = dict(Counter(dataListForCurrentTrack))
            for ele in expertiseLevels:
                if (ele not in expertiseByTrack[track]):
                    expertiseByTrack[track][ele] = 0

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
        print parsedResult['expertiseSR']
        # print parsedResult['averageScoreSR']
        # print ("====================================")

        return parsedResult