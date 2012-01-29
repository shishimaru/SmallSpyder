class Site:
    def __init__(self, url, title, wordList):
        self.url = url
        #self.title = title
        self.surfaceList = []
        self.posList = []
        
        for word in wordList:
            self.surfaceList.append(word[0])
            self.posList.append(word[1])