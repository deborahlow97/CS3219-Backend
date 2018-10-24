'''
Represents data from an uploaded csv file
'''
class CsvData:
    def __init__(self, type, dataDictionary, inputFiles):
        self.infoType = type
        self.data = dataDictionary
        self.csvFiles = inputFiles

    def setOrder(self, order):
        self.order = order
    
    def setInfo(self, info):
        self.info = info
        