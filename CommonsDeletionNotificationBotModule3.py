########################################################
#Module 3 : Notifying the wikipedia articles when
#           images associated with them are nominated for deletion
#           from commons but were kept
########################################################

import pywikibot
import re

commons=pywikibot.Site('commons','commons')
enwiki=pywikibot.Site('en')

count=0

def parseCategory(catName):
       # print(catPrefix)
        try:
                catSelected = pywikibot.Category(commons, 'Category:' + catName)
                catGenerator = catSelected.subcategories()
                for catDR in catGenerator:
                        print (catDR.title())
                        catGenerator2=catDR.subcategories()
                        for catDR2 in catGenerator2:
                            print ("\t"+catDR2.title())
                            for page in catDR2.articles():
                                notifyLinkedArticles(page)
                        for page in catDR.articles():
                            notifyLinkedArticles(page)
                print(count)
        except Exception as e:
            print(e)
            pass

def notifyLinkedArticles(page):
    global count
    try:
        if 'File:' in str(page) or 'Image:' in str(page):
            fileName=str(page).replace('[[commons:Commons:Deletion requests/','')
            fileName=fileName.replace(']]','')
            fileName=fileName.replace('[[commons:','')
            filePage=pywikibot.Page(commons,fileName)
            print(str(fileName))
            if filePage.exists():
                usages=[]
                print("Usages: ")
                for usage in enwiki.imageusage(filePage):
                    if 'Talk:' not in str(usage):
                        print(str(usage))
                        talkPage=usage.toggleTalkPage()
                        if talkPage.exists():
                            talkPageContent=talkPage.get()
                        else:
                            talkPageContent=""
                        #check if already notified for non deletion
                        test=re.search("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.\n:This image has been decided to be kept.\n:Message automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                        if test is None:#if not notified
                            #check if already notified for deletion nomination
                            test=re.search("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                            if test is not None:#if notified for deletion nomination
                                replaceText=test.group(0)+"\n:This image has been decided to be kept.\n:Message automatically deposited by a robot - -~~~~."
                                talkPageContent=re.sub("== File nominated for deletion on commons == \n The file ''\[\[:c:"+fileName+"\]\]'' has been nominated for deletion on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",replaceText,talkPageContent)
                                talkPage.put(talkPageContent,"File nominated for deletion and kept")#write to the talk page of the article
                            else: #if not notified for deletion nomination
                                test=re.search("\n== File nominated for deletion on commons ==\n The file ''\[\[:c:"+fileName+"\]\]'' used in this article has been nominated for deletion but was kept\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",talkPageContent)
                                if test is None:
                                    talkPageContent+="\n== File nominated for deletion on commons ==\n The file ''[[:c:"+fileName+"]]'' used in this article has been nominated for deletion but was kept\nMessage automatically deposited by a robot - -~~~~."
                                    talkPage.put(talkPageContent,"File nominated for deletion and kept")#write to the talk page of the article
                    usages.append(usage)
                if len(usages) > 0:
                    count=count+1
                    print(str(count)+". "+fileName + " Page: " + str(filePage) + " Usages in en wikipedia: " + str(len(usages)))
                else:
                    print("No usage in en wikipedia")
    except Exception as e:
        print(e)
        pass
        
            

parseCategory("Deletion requests/kept")
