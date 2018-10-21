'''
Represents data from an uploaded csv file
'''
class CsvData:
    def __init__(self, dataDictionary, inputFile):
        self.data = dataDictionary
        self.csvFile = inputFile
