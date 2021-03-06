########################################################
# Module 2 : Notifying the wikipedia articles when
#           images associated with them are deleted
#           from commons
########################################################
import logging
import re

import bs4
import pywikibot
import requests

wikimedia_commons = pywikibot.Site('commons', 'commons')
english_wikipedia = pywikibot.Site('en')


deletion_log_url = 'https://commons.wikimedia.org/w/index.php?title=' \
                   'Special:Log&limit=2000&type=delete&subtype=delete'
stop_flag = False

logging.basicConfig(filename="deletion.log", format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(pywikibot.logging.INFO)


# extracts file names from html tags
def get_file_names():
    response = requests.get(deletion_log_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return [a.text for a in soup.select('a.new')]


# finds usages of files and notifies the corresponding articles
def notify_articles(ui):
    global stop_flag
    print_line(ui)
    ui.listWidget.addItem("Notifying articles about deletion of images")
    print_line(ui)
    file_name_list = get_file_names()
    logger.info("files retrieved: " + str(len(file_name_list)))
    print("Total number of entries : " + str(len(file_name_list)))
    count = 0

    for file_name in file_name_list:
        try:
            usage_count = 0
            if 'Commons:Deletion requests/File:' in file_name or 'File:' in file_name:  # if it is a file
                count = count + 1
                file_name = file_name.replace('Commons:Deletion requests/', '')
                page = pywikibot.Page(wikimedia_commons, file_name)
                print("\n" + file_name)
                ui.listWidget.addItem(file_name)
                logger.info(file_name)
                print("Usages:")
                ui.listWidget.addItem("Usages:")
                logger.info("Usages:")

                for usage in english_wikipedia.imageusage(page):
                    if 'Talk:' not in str(usage):  # if usage is not a talk page
                        print(str(usage))
                        ui.listWidget.addItem(str(usage))
                        logger.info(str(usage))
                        talk_page = usage.toggleTalkPage()  # gets the talk page of the article
                        if talk_page.exists():  # if talk page exists
                            talk_page_content = talk_page.get()  # get the content of the talk page
                        else:  # else create a new talk page
                            talk_page_content = ""

                        # check if already notified for deletion
                        test = re.search("== File nominated for "
                                         "deletion on commons == "
                                         "\n The file ''\[\[:c:" + file_name + "\]\]'' "
                                         "used in this article has "
                                         "been nominated for deletion"
                                         " on Commons \n '''Reason:''' "
                                         "[\S\s]*\n '''Deletion request:''' [\S\s]*"
                                         "\nMessage automatically deposited "
                                         "by a robot - -[\S\s]* \(UTC\)\."
                                         "\n:This image has been "
                                         "deleted from Commons"
                                         "\n:Message automatically deposited "
                                         "by a robot - -[\S\s]* \(UTC\)\.",
                                         talk_page_content)

                        if test is None:  # if not notified
                            # check if already notified for deletion nomination
                            test = re.search("== File nominated for "
                                             "deletion on commons == "
                                             "\n The file ''\[\[:c:" + file_name + "\]\]'' "
                                             "used in this article "
                                             "has been nominated "
                                             "for deletion on "
                                             "Commons \n '''Reason:''' "
                                             "[\S\s]*\n '''Deletion request:''' [\S\s]*"
                                             "\nMessage automatically deposited"
                                             " by a robot - -[\S\s]* \(UTC\)\.",
                                             talk_page_content)

                            if test is not None:  # if notified for deletion nomination
                                replace_text = test.group(0) + "\n:This image has " \
                                                               "been deleted from Commons" \
                                                               "\n:Message automatically " \
                                                               "deposited by a robot - -~~~~."

                                talk_page_content = re.sub("== File nominated "
                                                           "for deletion on commons == "
                                                           "\n The file "
                                                           "''\[\[:c:" + file_name + "\]\]'' "
                                                           "used in this article has been "
                                                           "nominated for deletion on Commons "
                                                           "\n '''Reason:''' [\S\s]*\n "
                                                           "'''Deletion request:''' [\S\s]*"
                                                           "\nMessage automatically "
                                                           "deposited by a robot "
                                                           "- -[\S\s]* \(UTC\)\.",
                                                           replace_text, talk_page_content)

                                # write to the talk page of the article
                                talk_page.put(talk_page_content, "File deleted from Commons")
                                ui.listWidget.addItem("Talk page " + str(talk_page) + " saved")
                                logger.info("Talk page " + str(talk_page) + " saved")
                            else:  # if not notified for deletion nomination
                                test = re.search("\n==File Deleted from Commons== "
                                                 "\n The file ''\[\[:c:" + file_name + "\]\]''"
                                                 " used in this article has"
                                                 " been deleted from Commons"
                                                 "\nMessage automatically deposited by a "
                                                 "robot - -[\S\s]* \(UTC\)\.", talk_page_content)
                                if test is None:
                                    talk_page_content += "\n==File Deleted from " \
                                                         "Commons== \n The file " \
                                                         "''[[:c:" + file_name + "]]''" \
                                                         " used in this article" \
                                                         " has been deleted from Commons" \
                                                         "\nMessage automatically " \
                                                         "deposited by a robot - -~~~~."

                                    # write to the talk page of the article
                                    talk_page.put(talk_page_content, "File deleted from Commons")
                                    ui.listWidget.addItem("Talk page " + str(talk_page) + " saved")
                                    logger.info("Talk page " + str(talk_page) + " saved")

                        usage_count = usage_count + 1
                        if stop_flag:
                            break
                print(usage_count)
                if usage_count > 0:
                    ui.listWidget.addItem("Total Usages : " + str(usage_count))
                    logger.info("Total Usages : " + str(usage_count))
                else:
                    ui.listWidget.addItem("No usage in Wikipedia articles")
                    logger.info("No usage in Wikipedia articles")

                print_line(ui)

        except Exception as e:
            print(str(e))
        if stop_flag:
            break

    print(count)
    ui.listWidget.addItem("Bot Terminated")
    logger.info("Bot Terminated")
    stop_flag = False
    print_line(ui)
    ui.listWidget.scrollToBottom()
    ui.pushButton_1.setDisabled(False)
    ui.pushButton_2.setDisabled(False)
    ui.pushButton_3.setDisabled(False)


def stop(ui):
    global stop_flag
    stop_flag = True
    ui.listWidget.addItem("Bot Termination invoked. Please wait...")
    ui.pushButton_5.setDisabled(True)


def print_line(ui):
    ui.listWidget.addItem("==========================================================")
    ui.listWidget.scrollToBottom()
# notify_articles()
