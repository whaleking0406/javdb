import re
import json
import os
import requests
import cloudscraper
import constant
from lxml import etree

def get_html(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    html = response.text
    return html



def parse_title(html):
    return html.xpath('//strong[@class="current-title"]/text()')[0]



def parse_rating(html):
    rating_string = html.xpath('//strong[contains(text(),"評分:")]/following-sibling::span/text()')[0]
    ret = ''
    for i in rating_string:
        if i.isdigit() or i.isspace() or i == '.':
            ret += i
            continue
        break
    # Rating from JavDb is n/5. Convert to 10-based and 1 digit after decimal.
    return round(float(ret) * 2, 1)



def parse_summary(html):
    return "添加簡介"



def parse_backdrop(html):
    ret = []
    result = html.xpath('//a[@class="cover-container"]/img/@src')
    for i in result:
        if i != "":
            ret.append(i)
    return ret



def parse_poster(html):
    ret = []
    result = html.xpath('//a[@class="cover-container"]/img/@src')
    for i in result:
        if i != "":
            i = i.replace('covers', 'thumbs')
            ret.append(i)
    return ret



# Returns an array of string.
def parse_genre(html):
    return html.xpath('//strong[contains(text(),"類別:")]/following-sibling::span/a/text()')



def parse_release_date(html):
    return html.xpath('//strong[contains(text(),"日期:")]/following-sibling::span/text()')[0]



# Returns an array of string.
def parse_actors(html):
    return html.xpath('//strong[contains(text(),"演員:")]/following-sibling::span/a/text()')



# Returns an array of string.
def parse_writers(html):
    return html.xpath('//strong[contains(text(),"片商:")]/following-sibling::span/a/text()')


# Returns an array of string.
def parse_directors(html):
    return html.xpath('//strong[contains(text(),"導演:")]/following-sibling::span/a/text()')



# Crawl the web contents based on a given `key`. They `key` should be something that looks like ABC-123.   
def crawl_from_db(key):
    try:
        # Constrcut the search URL.
        htmlcode = get_html('https://javdb.com/search?q=' + key + '&f=all')
        html = etree.fromstring(htmlcode, etree.HTMLParser())

        # Fetch all the `item`s elements.
        counts = len(html.xpath("//div[@class='item']"))

        if counts != 0:
            for idx in range(1, counts + 1):
                serial_number = html.xpath("//div[@class='item'][" + str(idx) + "]/a/div[@class='video-title']/strong/text()")[0]
                serial_number = serial_number.upper().replace('_', '')
                key = key.upper().replace('_', '')
                if serial_number == key:
                    # JavDb has a special tag that's used for a movie. Parse it.
                    tag  = html.xpath("//div[@class='item'][" + str(idx) + "]/a/@href")[0]
                    return 'https://javdb.com/' + tag + '?locale=zh'
                return 'not found'
        return 'not found'

    except Exception as error_message:
        print('Error in crawl_from_db: ' + str(error_message))

    return ''



def main(key):
    try:
        result_url = crawl_from_db(key)

        if result_url == 'not found':
            raise Exception('Movie data not found in JavDb. Search key: ' + key)

        htmlcode = get_html(result_url)
        # print(htmlcode)
        html = etree.fromstring(htmlcode, etree.HTMLParser())

        ret = {
            'title': parse_title(html),
            'tagline': key,
            'original_available': parse_release_date(html),
            'summary': parse_summary(html),
            'genre': parse_genre(html),
            # `certificate` is optional.
            'actor': parse_actors(html),
            'writer': parse_writers(html),
            'director': parse_directors(html),
            'poster': parse_poster(html),
            'backdrop': parse_backdrop(html),
            'rating': parse_rating(html),
        }
    except Exception as error_message:
        print('Error in main: ' + str(error_message))
        ret = {}
    # print(ret)
    return ret
