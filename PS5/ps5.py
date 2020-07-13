# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz
import string
from datetime import datetime

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

class NewsStory(object):
    def __init__(self,guid,title,description,link,pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate





#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger
class PhraseTrigger(Trigger):

    def __init__(self, phrase):
        self.phrase = phrase.lower()

    def get_phrase(self):
        return self.phrase

    def __str__(self):
        return str(self.get_phrase())

    def is_phrase_in(self, text):
        """
        Takes in a string argument text as an input
        Returns True if the whole phrase is in the present
        text and False otherwise
        """
        # First lets remove all punctuation from text
        for punctuation in string.punctuation:
            if punctuation in text:
                text = text.replace(punctuation, ' ')

        # Next get all the words as items in a list and apply the join method
        # (this removes multiple white spaces)
        text_list = text.split()
        text = ' '.join(text_list)

        # Deal with plurals
        if self.phrase + 's' in text.lower():
            return False

        return self.phrase in text.lower()

# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):

    def evaluate(self, story):
        return self.is_phrase_in(text=story.get_title())


# Problem 4
class DescriptionTrigger(PhraseTrigger):

    def evaluate(self, story):
        return self.is_phrase_in(text=story.get_description())


# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger):
    def __init__(self, time):
        self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S").replace(tzinfo=pytz.timezone('EST'))

    def get_time(self):
        return self.time




# Problem 6
class BeforeTrigger(TimeTrigger):

    def evaluate(self, story):

        trigger_time = self.get_time()
        pub_date = story.get_pubdate()
        # check if story datetime is naive and if it is convert to aware so we can compare it
        if pub_date.tzinfo == None:
            pub_date = pub_date.replace(tzinfo=pytz.timezone('EST'))

        return pub_date < trigger_time


class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        trigger_time = self.get_time()
        pub_date = story.get_pubdate()
        if pub_date.tzinfo == None:
            pub_date = pub_date.replace(tzinfo=pytz.timezone('EST'))
        return pub_date > trigger_time



# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger

    def evaluate(self, story):
        trigger = self.trigger
        return not trigger.evaluate(story)

# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self,trigger1,trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self,story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)
# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self,story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)


#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """

    trigger_stories = []
    for news_story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(news_story)==True:
                trigger_stories.append(news_story)
    return trigger_stories



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """

    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)


    trigger_dict = {}
    trigger_list = []

    for line in lines:
        split_line = line.split(",")

        if 'ADD' not in split_line:
            trigger_name = split_line[0]
            trigger_type = split_line[1]


            if trigger_type == 'TITLE':
                trigger_dict[trigger_name] = TitleTrigger(split_line[2])

            elif trigger_type == 'DESCRIPTION':
                trigger_dict[trigger_name] = DescriptionTrigger(split_line[2])

            elif trigger_type == 'AFTER':
                trigger_dict[trigger_name] = AfterTrigger(split_line[2])

            elif trigger_type == 'BEFORE':
                trigger_dict[trigger_name] = BeforeTrigger(split_line[2])

            elif trigger_type == 'NOT':
                trigger_dict[trigger_name] = NotTrigger(split_line[2])

            elif trigger_type == 'AND':
                trigger_dict[trigger_name] = AndTrigger(split_line[2], split_line[3])

            elif trigger_type == 'OR':
                trigger_dict[trigger_name] = OrTrigger(split_line[2], split_line[3])

        else:
            split_line.pop([0])
            for trigger_name in split_line:
                trigger_list.append(trigger_dict[trigger_name])

    return trigger_list










SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Biden")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1,t4]

        # # Problem 11
        # # TODO: After implementing read_trigger_config, uncomment this line
        # triggerlist = read_trigger_config('triggers.txt')
        #
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            # stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
