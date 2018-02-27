########################################################
#Module 1 : Notifying the wikipedia articles when
#           images associated with them are nominated
#           for deletion on commons
########################################################

import pywikibot, mwparserfromhell
import hashlib, os

cachePath='E:/bot/'
commons=pywikibot.Site('commons','commons')
enwiki=pywikibot.Site('en')


#for finding the usage of a particular image in wikipedia articles
def findusage(page, type):
        try:
                first=True
                usages=[]
                for usage in enwiki.imageusage(page):
                        if first:
                                first=False
                        usages.append(usage)
                if not first:
                        textFile,alreadyTraced=readDesc(page)
                        wikicode = mwparserfromhell.parser.Parser().parse(textFile)
                        templates = wikicode.filter_templates()
                        deleteTemplate=None
                        if type=="DR":
                                templateList=['delete','del','deletebecause','puf','ffd']
                        if type=="nsd":
                                templateList=['nsd','no source since','no_source_since']
                        if type=="nld":
                                templateList=['nld','no license since','no_license_since']
                        if type=="npd":
                                templateList=['npd','no permission since','no_permission_since']
                        for template in templates:
                                if template.name.lower().strip() in templateList:
                                        deleteTemplate=template
                                        break
                        return usages, deleteTemplate, alreadyTraced
        except:
                pass
        return None, None, None

def readDesc(page):
        try:
                global cachePath
                cacheFile=hashlib.sha1(page.title().encode('utf-8')).hexdigest()
                if os.path.isfile(cachePath+cacheFile):
                        print(page.title() + " in cache : " + cacheFile)
                        f=open(cachePath+cacheFile,'r')
                        return f.read(), True
                else:
                        f=open(cachePath+cacheFile,'w',encoding="utf8")
                        text=page.get()
                        f.write(text)
                        return text, False
        except:
                pass
		
	
	
def articles(catDR, type):
        try:
                for page in catDR.articles():
                        usages, deleteTemplate, alreadyTraced = findusage(page, type)
                        print(deleteTemplate)
                        if deleteTemplate is not None:
                                if usages is not None and len(usages) > 0:
                                        print(page, usages,)
                                        imagepath=str(page).replace('commons','')
                                        imagepath=imagepath.replace('[[File:','[[:c:File:')
                                        imagepath=imagepath.replace('[[:File:','[[:c:File:')
                                        reason, subpage, date=parseTemplate(deleteTemplate, type)
                                        # main space
                                        counter=0
                                        for linkedpage in usages:
                                                counter+=1
                                                # no more than 10 pages to avoid a flood if the image is very used
                                                if counter==10:
                                                        break
                                                if linkedpage.namespace()==0 and not alreadyTraced:
                                                        talkPage=linkedpage.toggleTalkPage()
                                                        if talkPage.exists():
                                                                textTalkPage=talkPage.get()
                                                        else:
                                                                textTalkPage=""
                                                        # add a message to the associated talk page
                                                        textTalkPage+="\n== File nominated for deletion on commons == \n The file ''%s'' has been nominated for deletion on Commons \n '''Reason:''' %s \n '''Deletion request:''' %s \nMessage automatically deposited by a robot - -~~~~." % (imagepath, reason, subpage)
                                                        talkPage.put(textTalkPage, "File proposed for deletion")
        except:
                pass
				

def parseTemplate(deleteTemplate, type):
        try:
                reason='Not defined'
                subpage='Not defined'
                date='Not defined'
                if deleteTemplate is not None:
                        if type == "DR":
                                if deleteTemplate.has('reason'):
                                        print ("reason : " + str(deleteTemplate.get('reason').value))
                                        reason = str(deleteTemplate.get('reason').value)
                                        reason = reason.replace('{{','{{m|').replace('[[COM:','[[:c:COM:')
                                        reason = reason.replace('[[Category:','[[:Category:')
                                        reason = reason.replace('[[Commons:','[[:c:Commons:')
                                        reason = reason.replace('[[Com:','[[:c:Com:')
                                        reason = reason.replace("\n"," ")
                                if deleteTemplate.has('subpage'):
                                        subpage='[[:commons:Commons:Deletion_requests/' + str(deleteTemplate.get('subpage').value).strip() + '|link]]'
                        else:
                                # for nsd / nld / npd there is no subpage, the reason is directly on the image
                                if type=="nsd":
                                        reason="No source indicated"
                                if type=="nld":
                                        reason="No license indicated"
                                if type=="npd":
                                        reason="No permission indicated"
                                
                                
                        if deleteTemplate.has('month'):
                                date=str(deleteTemplate.get('month').value).strip()
                        if deleteTemplate.has('day'):
                                date+=" "+str(deleteTemplate.get('day').value).strip()
                        if deleteTemplate.has('year'):
                                date+=" "+str(deleteTemplate.get('year').value).strip()
        except:
                pass
        return reason, subpage, date


def parseCategory(catName, catPrefix, type):
        try:
                catSelected = pywikibot.Category(commons, 'Category:%s' % catName)
                catGenerator = catSelected.subcategories()

                for catDR in catGenerator:
                        print (catDR.title())
                        if catDR.title().startswith('Category:%s' % catPrefix):
                                articles(catDR, type)
        except:
                pass


#parseCategory("Media without a source","Media without a source as of","nsd")
#parseCategory("Media missing permission","Media missing permission as of","npd")
#parseCategory("Media without a license","Media without a license as of","nld")
parseCategory("Deletion requests","Deletion requests","DR")


