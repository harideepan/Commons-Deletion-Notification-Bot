########################################################
# Module 3 : Notifying the wikipedia articles when
#           images associated with them are
#           nominated for deletion from commons,
#           but were kept
########################################################

import re

import mwparserfromhell
import pywikibot

wikimedia_commons = pywikibot.Site('commons', 'commons')
english_wikipedia = pywikibot.Site('en')
count = 0


# parses the given category and it subcategories
def parse_category(category):
    try:
        # Top level category.
        selected_category = pywikibot.Category(wikimedia_commons, 'Category:' + category)

        # first level categories
        subcategories1 = selected_category.subcategories()
        for category1 in subcategories1:
            print(category1.title())

            # second level categories
            subcategories2 = category1.subcategories()
            for category2 in subcategories2:
                print("\t" + category2.title())
                for page in category2.articles():  # image files in second level categories
                    notify_linked_articles(page)

            for page in category1.articles():  # image files in first level categories
                notify_linked_articles(page)
        print(count)
    except Exception as e:
        print(e)
        pass


def get_author_name(page):
    author = "Not defined"
    information_template = None
    try:
        text = page.get()
        wiki_code = mwparserfromhell.parser.Parser().parse(text)  # extracts the wiki code
        templates = wiki_code.filter_templates()  # filter the templates from the wiki code
        for template in templates:
            if "information" in template.name.lower().strip():
                information_template = template

        if information_template is not None:
            if information_template.has('author'):
                print("Author : " + str(information_template.get('author').value))
                author = str(information_template.get('author').value)

    except Exception as e:
        print(e)
    return author


def notify_linked_articles(page):
    global count
    try:
        if 'File:' in str(page) or 'Image:' in str(page):

            file_name = str(page).replace('[[commons:Commons:Deletion requests/', '')
            file_name = file_name.replace(']]', '')
            file_name = file_name.replace('[[commons:', '')
            file_page = pywikibot.Page(wikimedia_commons, file_name)
            print(str(file_name))
            if file_page.exists():
                usages = []

                # notify user who uploaded the image
                author = get_author_name(file_page)
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

                        # check if already notified for non deletion
                        test = re.search("== File nominated for deletion on commons == "
                                         "\n The file ''\[\[:c:" + file_name + "\]\]'' uploaded by you "
                                         "has been nominated for deletion "
                                         "on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*"
                                         "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\."
                                         "\n:This image has been decided to be kept."
                                         "\n:Message automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                         author_talk_page_content)

                        if test is None:  # if not notified
                            # check if already notified for deletion nomination
                            test = re.search("== File nominated for deletion on commons == "
                                             "\n The file ''\[\[:c:" + file_name + "\]\]'' uploaded by you "
                                             "has been nominated for "
                                             "deletion on Commons \n '''Reason:''' [\S\s]*"
                                             "\n '''Deletion request:''' [\S\s]*"
                                             "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                             author_talk_page_content)

                            if test is not None:  # if notified for deletion nomination
                                replace_text = test.group(0) + "\n:This image has been decided to be kept." \
                                                              "\n:Message automatically deposited by a robot - -~~~~."

                                talk_page_content = re.sub("== File nominated for deletion on commons == "
                                                           "\n The file ''\[\[:c:" + file_name + "\]\]'' uploaded by "
                                                           "you has been "
                                                           "nominated for deletion on Commons "
                                                           "\n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*"
                                                           "\nMessage automatically deposited by a robot "
                                                           "- -[\S\s]* \(UTC\)\.",
                                                           replace_text, author_talk_page_content)

                                # write to the talk page of the article
                                author_talk_page.put(talk_page_content, "File nominated for deletion and kept")

                            else:  # if not notified for deletion nomination
                                test = re.search("\n== File nominated for deletion on commons =="
                                                 "\n The file ''\[\[:c:" + file_name + "\]\]'' uploaded by you "
                                                 "has been nominated for deletion but was kept"
                                                 "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                                 author_talk_page_content)

                                if test is None:
                                    author_talk_page_content += "\n== File nominated for deletion on commons ==" \
                                                         "\n The file ''[[:c:" + file_name + "]]'' uploaded by " \
                                                         "you has been nominated for deletion but was kept" \
                                                         "\nMessage automatically deposited by a robot - -~~~~."

                                    # write to the talk page of the article
                                    author_talk_page.put(author_talk_page_content, "File nominated for"
                                                                                   " deletion and kept")

                    else:
                        print("Author page does not exists")

                print("Usages: ")
                # notify the wikipedia articles using the image
                for usage in english_wikipedia.imageusage(file_page):
                    if 'Talk:' not in str(usage):
                        print(str(usage))
                        talk_page = usage.toggleTalkPage()
                        if talk_page.exists():
                            talk_page_content = talk_page.get()
                        else:
                            talk_page_content = ""

                        # check if already notified for non deletion
                        test = re.search("== File nominated for deletion on commons == "
                                         "\n The file ''\[\[:c:" + file_name + "\]\]'' used in this article "
                                         "has been nominated for deletion "
                                         "on Commons \n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*"
                                         "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\."
                                         "\n:This image has been decided to be kept."
                                         "\n:Message automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                         talk_page_content)

                        if test is None:  # if not notified
                            # check if already notified for deletion nomination
                            test = re.search("== File nominated for deletion on commons == "
                                             "\n The file ''\[\[:c:" + file_name + "\]\]'' used in this article "
                                             "has been nominated for "
                                             "deletion on Commons \n '''Reason:''' [\S\s]*"
                                             "\n '''Deletion request:''' [\S\s]*"
                                             "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                             talk_page_content)

                            if test is not None:  # if notified for deletion nomination
                                replace_text = test.group(0) + "\n:This image has been decided to be kept." \
                                                              "\n:Message automatically deposited by a robot - -~~~~."

                                talk_page_content = re.sub("== File nominated for deletion on commons == "
                                                           "\n The file ''\[\[:c:" + file_name + "\]\]'' "
                                                           "used in this article has been "
                                                           "nominated for deletion on Commons "
                                                           "\n '''Reason:''' [\S\s]*\n '''Deletion request:''' [\S\s]*"
                                                           "\nMessage automatically deposited by a robot "
                                                           "- -[\S\s]* \(UTC\)\.",
                                                           replace_text, talk_page_content)

                                # write to the talk page of the article
                                talk_page.put(talk_page_content, "File nominated for deletion and kept")

                            else:  # if not notified for deletion nomination
                                test = re.search("\n== File nominated for deletion on commons =="
                                                 "\n The file ''\[\[:c:" + file_name + "\]\]'' used in this article "
                                                 "has been nominated for deletion but was kept"
                                                 "\nMessage automatically deposited by a robot - -[\S\s]* \(UTC\)\.",
                                                 talk_page_content)

                                if test is None:
                                    talk_page_content += "\n== File nominated for deletion on commons ==" \
                                                         "\n The file ''[[:c:" + file_name + "]]'' used in this " \
                                                         "article has been nominated for deletion but was kept" \
                                                         "\nMessage automatically deposited by a robot - -~~~~."

                                    # write to the talk page of the article
                                    talk_page.put(talk_page_content, "File nominated for deletion and kept")

                    usages.append(usage)

                if len(usages) > 0:
                    count = count + 1
                    print(str(count) + ". " + file_name +
                          " Page: " + str(file_page) +
                          " Usages in English wikipedia: " + str(len(usages)))
                else:
                    print("No usage in English wikipedia")

    except Exception as e:
        print(e)
        pass


parse_category("Deletion requests/kept")
