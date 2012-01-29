#!/usr/bin/env python
#encoding:utf-8

import pickle
import cgi
import os
from result import Site

fin = open("spy.pkl", "rb")
BR = "<br>"
print '''content-type: text/html;charset=utf-8\n'''

def search(keywords):
    sites = []
    while True:
        site = None
        try:
            site = pickle.load(fin)
        except:
            break
        
        if site:
            matchNumber = 0
            for keyword in keywords:
                if keyword in site.surfaceList:
                    matchNumber += 1
                else:
                    break
        
            if matchNumber == len(keywords):
                sites.append(site)

        else:
            break
    fin.close()

    url_result = {}
    for site in sites:
        for surface in site.surfaceList:
            if surface in keywords:
                if url_result.get(site.url) == None:
                    url_result[site.url] = 1
                else:
                    url_result[site.url] += 1

    print url_result,"<br>"

    urlList = sorted(url_result.items(), key=lambda(k,v): (v,k), reverse=True)
    print urlList,"<br>"

    for url in urlList:
        print "<a href=\"%s\">[%d] %s</a><br>" % (url[0], url[1], url[0])
                
    
if __name__ == "__main__":
    if os.environ.has_key("QUERY_STRING"):
        query = cgi.parse_qs(os.environ["QUERY_STRING"])
    else:
        query = {"q":["python"]}
        
    print "<h3>query=%s</h3>" % query        
    if query and query.has_key("q"):
        keywords = query["q"]
        search(keywords)
    else:
        print "<h1>usage : ?q=<i>keyword</i></h1>"
    