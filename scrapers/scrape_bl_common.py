#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from bs4 import BeautifulSoup
import re
import scrape_common as sc


def get_latest_bl_bulletin_url():
    return get_all_bl_bulletin_urls()[0]


def get_all_bl_bulletin_urls():
    news_url = 'https://www.baselland.ch/politik-und-behorden/direktionen/volkswirtschafts-und-gesundheitsdirektion/amt-fur-gesundheit/medizinische-dienste/kantonsarztlicher-dienst/aktuelles/medienmitteilungen-1'
    news_content = sc.download(news_url, silent=True)
    soup = BeautifulSoup(news_content, 'html.parser')

    bulletins = soup.find_all('a', href=re.compile(r'.*/coronavirus-wochenbulletin.*'))
    bulletin_urls = []
    for bulletin in bulletins:
        bulletin_urls.append(bulletin.get('href'))
    return bulletin_urls


def strip_bl_bulletin_numbers(content):
    content = re.sub(r'(\d+)’(\d+)', r'\1\2', content)
    content = re.sub(r'(\d+)\'(\d+)', r'\1\2', content)
    return content


def parse_bl_date(s):
    row_date = s.replace('-', '.')
    row_date = s.replace('/', '.')
    parts = row_date.split('.')
    s_date = datetime.datetime(day=int(parts[0]), month=int(parts[1]), year=int(parts[2]))
    key = s_date.date().isoformat()
    return (key, row_date)
