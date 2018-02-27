########################################################
#Module 2 : Notifying the wikipedia articles when
#           images associated with them are deleted
#           from commons
########################################################

import requests
import bs4
import pywikibot
import re

commons=pywikibot.Site('commons','commons')
enwiki=pywikibot.Site('en')

#deletion log URL
index_url = 'https://commons.wikimedia.org/w/index.php?title=Special:Log&offset=&limit=20&type=delete&user=&page=&tagfilter=&subtype=delete'

#extracts filenames from html tags
def getFileNames():
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text,"html.parser")
    #return soup
    return [a.text for a in soup.select('a.new')]

#finds usages of files and notifies the corresponding articles
def notifyArticles():
    List=getFileNames()
    print(len(List))
    count=0
    ucount=0
    for fileName in List:
        try:
            ucount=0;
            if  'Commons:Deletion requests/File:' in fileName or 'File:' in fileName:
                count=count+1
                fileName=fileName.replace('Commons:Deletion requests/','')
                page=pywikibot.Page(commons,fileName)
                print("\n"+fileName)
                print("Usages:")
                for usage in enwiki.imageusage(page):
                    if 'Talk:' not in str(usage): #if usage is not a talk page
                        print(str(usage))
                        talkPage=usage.toggleTalkPage() #gets the talk page of the article
                        if talkPage.exists():#if talk page exists
                            talkPageContent=talkPage.get() #get the content of the talk page
                        else:#else create a new talk page
                            talkPageContent=""
                        #check if already notified for deletion
                        test=re.search("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.\n:This image has been deleted from Commons\n:Message automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                        if test is None:#if not notified
                            #check if already notified for deletion nomination
                            test=re.search("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                            if test is not None:#if notified for deletion nomination
                                replaceText=test.group(0)+"\n:This image has been deleted from Commons\n:Message automatically deposited by a robot - -~~~~."
                                talkPageContent=re.sub("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",replaceText,talkPageContent)
                                talkPage.put(talkPageContent,"File deleted from Commons")#write to the talk page of the article
                            else: #if not notified for deletion nomination
                                test=re.search("\n==File Deleted from Commons== \n The file ''\[\[:c:"+fileName+"\]\]'' used in this article has been deleted from Commons\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                                if test is None:
                                    talkPageContent+="\n==File Deleted from Commons== \n The file ''[[:c:"+fileName+"]]'' used in this article has been deleted from Commons\nMessage automatically deposited by a robot - -~~~~."
                                    talkPage.put(talkPageContent,"File deleted from Commons")#write to the talk page of the article
                        ucount=ucount+1
                print(ucount)
        except Exception as e:
            print(str(e))
    print(count)


notifyArticles()
