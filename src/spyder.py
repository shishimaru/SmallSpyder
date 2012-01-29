#!/usr/bin/env python
#coding:utf-8

import urllib,urllib2
import urlparse
from xml.dom import minidom
import sys
import pickle
from result import Site
import BeautifulSoup

appid = "GdHkQHKxg64J4CDx5G3x6SBBAOOvqgt3oXjjMRdMN_WUOoJRToDWFvDUXOlaf.jd7LOsVg--"
url_jlp = "http://jlp.yahooapis.jp/MAService/V1/parse"
db_filename = "spy.pkl"

def morph(sentence, results = "ma", filter = "1|2|3|4|5|9|10"):
    sentence = sentence.encode("utf-8")
    params = urllib.urlencode({"appid":appid,
                               "result":results,
                               "filter":filter,
                               "sentence":sentence})
    res = urllib2.urlopen(url_jlp, params)
    doc = minidom.parseString(res.read())
    #print doc.toxml("utf-8")
    
    res.close()
    # get word list
    wordList = []
    wordEs = doc.getElementsByTagName("word")
    for wordE in wordEs:
        surface = wordE.getElementsByTagName("surface")[0]
        pos = wordE.getElementsByTagName("pos")[0]
        wordList.append((surface.firstChild.nodeValue, pos.firstChild.nodeValue))
    
    return wordList
            
def save(url, title, wordList):
    s = Site(url, title, wordList)
    fout = open(db_filename, "ab")
    p = pickle.Pickler(fout)
    p.dump(s)
    fout.close()            

def getSoup(url):
    try:
        res = urllib2.urlopen(url)
        headers = res.info()
        contentType = headers.getheader("content-type")
        if "html" in contentType.lower(): 
            return BeautifulSoup.BeautifulSoup(res.read(), convertEntities = "html")
        else:
            return None
    except:
        sys.stderr.write("http error : " + url + "\n")
        pass
    return None
    
def getNavigableStrings(soup):
    if isinstance(soup, BeautifulSoup.NavigableString):
        if type(soup) not in (BeautifulSoup.Comment,
                              BeautifulSoup.Declaration) and soup.strip():
            yield soup
    elif soup.name not in ('script', 'style'):
        for c in soup.contents:
            for g in getNavigableStrings(c):
                yield g
def getHtmlStringContents(soup):
    #contents = "\n".join(getNavigableStrings(soup))
    contents = []
    for ss in getNavigableStrings(soup):
        contents.append(ss)
    return contents

def visitedAlready(url):
    try:
        fin = open(db_filename, "rb")
    except:
        return False
    
    res = False
    if fin:
        while True:
            site = None
            try:
                site = pickle.load(fin)
            except:
                pass
            
            if site == None:
                res = False
                break
            else:
                if url == site.url:
                    res = True
                    break
    return res

def spyAndSave(url, depth):
    if depth < 0:
        return
    
    soup = getSoup(url)
    if soup == None:
        return
    #print soup.prettify()
    
    if visitedAlready(url):
        sys.stderr.write("visited already : " + url + "\n")
    else:
        titles = soup("title")
        title = ""
        if titles and len(titles):
            title = soup("title")[0].getString()
            
        
        print "@", url, title, depth
        contents = getHtmlStringContents(soup)
        #print contents

        i = 0
        size = len(contents)
        tmpContents = ""
        for i in range(0, size, 100):
            print i
            if i + 100 > size:
                tmpContents = contents[i:]
            else:
                tmpContents = contents[i:i+100]
        
        wordList = morph("\n".join(tmpContents))
        save(url, title, wordList)
            
    # spy the refered page
    stopPath = [None, "#"]
    for aE in soup("a"):
        href = aE.get("href")
        if href in stopPath:
            continue
        
        resolved = urlparse.urljoin(url, href)
        if urlparse.urlsplit(url)[1] != urlparse.urlsplit(resolved)[1]:
            print "escape : " + resolved
            continue
        
        spyAndSave(resolved, depth-1)

if __name__ == "__main__":
    urls = []
    urls.append("http://www.python.jp/Zope")
    depth = 1

    for url in urls:
        print "processing : " + url
        spyAndSave(url, depth) 
    