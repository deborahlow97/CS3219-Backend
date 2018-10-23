'''
Represents data from an uploaded csv file
'''
class CsvData:
    def __init__(self, type, dataDictionary, inputFile):
        self.data = dataDictionary
        self.csvFile = inputFile
        self.infoType = type

    def getOrder(self):
        pass

    def getInfo(self):
        pass