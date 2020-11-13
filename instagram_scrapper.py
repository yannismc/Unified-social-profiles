import datetime
import time

import selenium.common.exceptions as sel_error
from selenium import webdriver
from bs4 import BeautifulSoup as bs

username = "Billios11"
posts_meta = get_posts_with_scrapping(username)
for p in posts_meta:
    try:
        clean_text, hashtags, img_url, like_count, shares_count, source, timestamp, mentions = extract_post_data(p)
        except AttributeError as ae:
            print("Could not extract due to, ", ae)
            continue
        except TypeError as te:
            print("Could not extract due to, ", te)
            continue

def get_posts_with_scrapping(username):
    browser = webdriver.Firefox(executable_path=r'/home/psyentist/Downloads/geckodriver')
    browser.get("https://www.instagram.com/" + username + "/?hl=en")
    lenOfPage = browser.execute_script(
       "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    scroll_count = 0
    while match is False and scroll_count < 5:  # default 200 -> 1232 statuses
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
    #posts_meta = bs(source_data, 'html.parser')
    #posts_meta = soup.findAll("article", {"class": "ySN3v"})
    posts_meta = soup.findAll("div", {"class": "v1Nh3"})
    browser.close()
    return posts_meta

def extract_post_data(p):
    post_path = p.find("a").get("href")
    browser = webdriver.Firefox(executable_path=r'/home/psyentist/Downloads/geckodriver')
    browser.get("https://www.instagram.com" + post_path + "?hl=en")
    post_source = browser.page_source
    post_html = bs(post_source, 'html.parser')
    browser.close()
    text = post_html.find("div", {"class": "C4VMK"}).find("span", recursive=False)
    clean_text = text.text
    print("clean_text", clean_text)
    mentions = extract_mentions_from_text(text)
    print("mentions", mentions)
    hashtags = extract_hashtags_from_text(text)
    print("hashtags", hashtags)
    timestamp_parent = post_html.find("time", {"class": "_1o9PC Nzb55"})
    timestamp = timestamp_parent['datetime']
    print("timestamp", timestamp)
    source = "https://www.instagram.com" + post_path + "?hl=en"
    print("source", source)
    # todo fix img urls
    img_html = p.find("img", {"class": "FFVAD"})
    img_url = None
    if img_html is not None:
        img_url = img_html['src']
    print("img_url", img_url)
    shares_count = like_count = 0
    likes_button = post_html.find("div", {"class": "Nm9Fw"})
    if likes_button is None:
        likes_button = post_html.find("span", {"class": "vcOH2"})
    print("likes_button", likes_button)
    likes_span = likes_button.find("span")
    print("likes_span", likes_span)
    likes = likes_span.contents
    print("likes", likes)
    if likes is not []:
        like_count = int(likes[0].replace(",", ""))
    print("likes_count", like_count)
    return clean_text, hashtags, img_url, like_count, shares_count, source, timestamp, mentions

def print_post_data(clean_text, hashtags, img_url, like_count, shares_count, source, timestamp):
    print("clean_text:\n\n",clean_text)
    print("timestamp:\n\n ", timestamp)
    print("source:\n\n",source)
    print("img_url\n\n",img_url)
    print("likes_count\n\n",like_count)
    print("shares_count:\n\n",shares_count)
    #print("mentions", mentions)
    print("hashtags", hashtags)

def before(string, substring):
    position = string.find(substring)
    if position == -1:
        return ''
    return string[0:position]


def extract_post_text(txt):
    cleaned_text = txt.find("span", {"class": ""})
    txt = ''
    for t in cleaned_text:
        txt += t.text

    return txt


def extract_mentions_from_text(text):
    mentions = []
    mentions_html = text.findAll("a", {"class": "notranslate"})
    i = 0
    if mentions_html is not None:
        for m in mentions_html:
            mentions.append(i)
            mentions[i] = m.contents[0]
            i+=1
    return mentions


def extract_hashtags_from_text(text):
    hashtags = []
    hashtags_html = text.findAll("a", {"class": "xil3i"})
    #print("hashtags_html", hashtags_html)
    i = 0
    if hashtags_html is not None:
        for h in hashtags_html:
            hashtags.append(i)
            hashtags[i] = h.contents[0]
            i+=1
            #hashtags = hashtags_html.contents
    return hashtags


def extract_timestamp_from_html(tstamp_html):
    return tstamp_html['datetime']


def extract_share_count_from_text(shares_text):
    before_text = before(shares_text.text.replace(",", ""), ' Share')
    if before_text.__contains__('K') :
        before_text = float(before(before_text, 'K'))*1000

    return int(before_text)

def remove_span(text):
        for sp in text.findAll('span'):
                sp.replaceWith('')
        return text
