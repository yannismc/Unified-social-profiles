import datetime
import time

import selenium.common.exceptions as sel_error
from selenium import webdriver
from bs4 import BeautifulSoup as bs

username = "Billios11"
posts_meta = get_posts_with_scrapping(username)
for p in posts_meta:
    try:
        clean_text, hashtags, img_url, like_count, mentions, shares_count, source, timestamp = extract_post_data(p)
    except AttributeError as ae:
            print("Could not extract due to, ", ae)
            continue
        except TypeError as te:
            print("Could not extract due to, ", te)
            continue

def get_posts_with_scrapping(username):
    browser = webdriver.Firefox(executable_path=r'/home/psyentist/Downloads/geckodriver')
    browser.get("https://www.facebook.com/pg/" + username + "/posts")
    lenOfPage = browser.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    scroll_count = 0
    while match is False and scroll_count < 20:  # default 200 -> 1232 statuses
        lastCount = lenOfPage
        time.sleep(5)  # 5secs for slow connections
        try :
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        except sel_error.JavascriptException as je:
            print("Could not scroll down, due to ", je)
            continue

        scroll_count += 1
        print(scroll_count)
        if lastCount == lenOfPage:
            match = True
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source
    # Throw your source into BeautifulSoup and start parsing!
    soup = bs(source_data, 'html.parser')
    posts_meta = soup.findAll("div", {"class": "userContentWrapper"})
    browser.close()
    return posts_meta

def extract_post_data(p):
    text = p.find("div", {"class": "userContent"})
    clean_text = extract_post_text(text)
    mentions = extract_mentions_from_text(text)
    hashtags = extract_hashtags_from_text(text)
    timestamp_html = p.find("abbr", {"class": "livetimestamp"})
    timestamp = extract_timestamp_from_html(timestamp_html)
    source_html = p.find("a", {"class": "_52c6"})
    source = None
    if source_html is not None:
        source = source_html['href']
    # todo fix img urls
    img_html = p.find("img", {"class": "scaledImageFitWidth"})
    img_url = None
    if img_html is not None:
        img_url = img_html['src']
    share_section = p.find("div", {"class": "UFIList"})
    shares_count = like_count = 0
    if share_section is None:
        shares_text = p.find("a", {"class": "_3rwx _42ft"})
        shares_count = extract_share_count_from_text(shares_text)

    if share_section is not None and shares_count == 0:
        likes = share_section.find("div", {"class": "UFILikeSentenceText"}).findChildren('span', recursive='false')
        like_count = 0
        if likes is not []:
            like_count = int(before(likes[0].text.replace(",", ""), ' others like this.').split(' ')[-1])
    return clean_text, hashtags, img_url, like_count, mentions, shares_count, source, timestamp

def print_post_data(clean_text, hashtags, img_url, like_count, mentions, shares_count, source, timestamp):
    print(clean_text)
    print("timestamp: ", timestamp)
    print(source)
    print(img_url)
    print(like_count)
    print(shares_count)
    print("mentions", mentions)
    print("hashtags", hashtags)

def before(string, substring):
    position = string.find(substring)
    if position == -1:
        return ''
    return string[0:position]

def extract_post_text(txt):
    cleaned_text = txt.findChildren('p', recursive='false')
    txt = ''
    for t in cleaned_text:
        txt += t.text

    return txt


def extract_mentions_from_text(text):
    mentions = []
    mentions_html = text.find("a", {"class": "profileLink"})
    if mentions_html is not None:
        mentions = mentions_html.contents
    return mentions


def extract_hashtags_from_text(text):
    hashtags = []
    hashtags_html = text.find("span", {"class": "_58cm"})
    if hashtags_html is not None:
        hashtags = hashtags_html.contents
    return hashtags


def extract_timestamp_from_html(tstamp_html):
    return tstamp_html['data-utime']


def extract_share_count_from_text(shares_text):
    before_text = before(shares_text.text.replace(",", ""), ' Share')
    if before_text.__contains__('K') :
        before_text = float(before(before_text, 'K'))*1000

    return int(before_text)

def remove_span(text):
        for sp in text.findAll('span'):
                sp.replaceWith('')
        return text
