########################################################
# Module 1 : Notifying the wikipedia articles when
#           images associated with them are nominated
#           for deletion on commons
########################################################

import hashlib
import os

import mwparserfromhell
import pywikibot

cache_path = 'E:/bot/'
wikimedia_commons = pywikibot.Site('commons', 'commons')
english_wikipedia = pywikibot.Site('en')


# notifies the articles associated with the images nominated for deletion
def notify_articles(category, type):
    try:
        for page in category.articles():
            usages, delete_template, information_template, already_traced = find_usage(page, type)
            if delete_template is not None:
                if usages is not None and len(usages) > 0:
                    print(page, usages)
                    image_path = str(page).replace('commons', '')
                    image_path = image_path.replace('[[File:', '[[:c:File:')
                    image_path = image_path.replace('[[:File:', '[[:c:File:')
                    reason, sub_page, date = parse_template(delete_template, type)

                    # notify the user who uploaded the image
                    author = get_author_name(information_template)
                    if not already_traced:
                        if "User:" in author:
                            author = author.replace("[[", "")
                            author = author.replace("]]", "")
                            author_page = pywikibot.Page(english_wikipedia, author)
                            if author_page.exists():
                                author_talk_page = author_page.toggleTalkPage()
                                if author_talk_page.exists():
                                    author_talk_page_content = author_talk_page.get()
                                else:
                                    author_talk_page_content = ""
                                author_talk_page_content += "\n== File nominated for deletion on commons == " \
                                                            "\n The file ''%s'' uploaded by" \
                                                            " you has been nominated for " \
                                                            "deletion on Commons \n '''Reason:''' %s \n " \
                                                            "'''Deletion Request:''' %s \nMessage automatically " \
                                                            "deposited by a robot - -~~~~." % \
                                                            (image_path, reason, sub_page)
                                author_talk_page.put(author_talk_page_content, "File proposed for deletion")

                    counter = 0
                    # notify the wikipedia articles using the image
                    for wikipedia_article in usages:
                        counter += 1
                        # no more than 10 pages to avoid a flood if the image is very used
                        if counter == 10:
                            break
                        if wikipedia_article.namespace() == 0 and not already_traced:
                            talk_page = wikipedia_article.toggleTalkPage()
                            if talk_page.exists():
                                talk_page_content = talk_page.get()
                            else:
                                talk_page_content = ""
                            # add a message to the associated talk page
                            talk_page_content += "\n== File nominated for deletion on commons == \n The file ''%s'' " \
                                                 "used in this article has been nominated for " \
                                                 "deletion on Commons \n '''Reason:''' %s \n " \
                                                 "'''Deletion request:''' %s \nMessage automatically deposited by a " \
                                                 "robot - -~~~~." % (image_path, reason, sub_page)
                            talk_page.put(talk_page_content, "File proposed for deletion")
    except Exception as e:
        print(e)
        pass


# gets the author name from information template of the image
def get_author_name(information_template):
    author = "Not defined"
    try:
        if information_template is not None:
            if information_template.has('author'):
                print("Author : " + str(information_template.get('author').value))
                author = str(information_template.get('author').value)
    except Exception as e:
        print(e)
    return author


# finds the usages of images
def find_usage(page, type):
    global template_list
    try:
        has_usage = False
        usages = []
        for usage in english_wikipedia.imageusage(page):
            if not has_usage:
                has_usage = True
            usages.append(usage)
        if has_usage:
            text_file, already_traced = read_description(page)
            wiki_code = mwparserfromhell.parser.Parser().parse(text_file)  # extracts the wiki code
            templates = wiki_code.filter_templates()  # filter the templates from the wiki code
            delete_template = None
            information_template = None

            if type == "DR":
                template_list = ['delete', 'del', 'deletebecause', 'puf', 'ffd']
            if type == "nsd":
                template_list = ['nsd', 'no source since', 'no_source_since']
            if type == "nld":
                template_list = ['nld', 'no license since', 'no_license_since']
            if type == "npd":
                template_list = ['npd', 'no permission since', 'no_permission_since']

            for template in templates:
                if template.name.lower().strip() in template_list:
                    delete_template = template
                if "information" in template.name.lower().strip():
                    information_template = template

            return usages, delete_template, information_template, already_traced
    except Exception as e:
        print(e)
        pass
    return None, None, None, None


# parses the description of the image
def read_description(page):
    try:
        global cache_path
        cache_file = hashlib.sha1(page.title().encode('utf-8')).hexdigest()
        if os.path.isfile(cache_path + cache_file):  # checks if the description of file already in cache
            print(page.title() + " in cache : " + cache_file)
            f = open(cache_path + cache_file, 'r')
            return f.read(), True
        else:  # adds the description to cache for later usage
            f = open(cache_path + cache_file, 'w', encoding="utf8")
            text = page.get()
            f.write(text)
            return text, False
    except Exception as e:
        print(e)
        pass


# extracts details from the delete template
def parse_template(delete_template, type):
    reason = 'Not defined'
    sub_page = 'Not defined'
    date = 'Not defined'
    try:
        if delete_template is not None:
            if type == "DR":  # if it is a deletion request
                if delete_template.has('reason'):
                    print("reason : " + str(delete_template.get('reason').value))
                    reason = str(delete_template.get('reason').value)  # extract the reason for deletion nomination
                    reason = reason.replace('{{', '{{m|').replace('[[COM:', '[[:c:COM:')
                    reason = reason.replace('[[Category:', '[[:Category:')
                    reason = reason.replace('[[Commons:', '[[:c:Commons:')
                    reason = reason.replace('[[Com:', '[[:c:Com:')
                    reason = reason.replace("\n", " ")
                if delete_template.has('subpage'):
                    sub_page = '[[:commons:Commons:Deletion_requests/' + str(
                        delete_template.get('subpage').value).strip() + '|link]]'
            else:
                # for nsd / nld / npd there is no sub-page, the reason is directly on the image
                if type == "nsd":
                    reason = "No source indicated"
                if type == "nld":
                    reason = "No license indicated"
                if type == "npd":
                    reason = "No permission indicated"

            # extract the date of deletion nomination
            if delete_template.has('month'):
                date = str(delete_template.get('month').value).strip()
            if delete_template.has('day'):
                date += " " + str(delete_template.get('day').value).strip()
            if delete_template.has('year'):
                date += " " + str(delete_template.get('year').value).strip()
    except Exception as e:
        print(e)
        pass
    return reason, sub_page, date


# Parses the given category and it's subcategories
def parse_category(category_name, category_prefix, type):
    try:
        selected_category = pywikibot.Category(wikimedia_commons, 'Category:%s' % category_name)
        subcategories = selected_category.subcategories()  # get the subcategories

        for category in subcategories:
            print(category.title())
            if category.title().startswith('Category:%s' % category_prefix):
                notify_articles(category, type)  # notify the articles using the images in this category
    except Exception as e:
        print(e)
        pass


parse_category("Deletion requests", "Deletion requests", "DR")
# parse_category("Media without a source", "Media without a source as of", "nsd")
# parse_category("Media missing permission", "Media missing permission as of", "npd")
# parse_category("Media without a license", "Media without a license as of", "nld")
