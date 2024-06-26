#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re
import sys
import requests
from bs4 import BeautifulSoup
import scrape_common as sc
import scrape_vd_common as svc


def parse_html():
    # https://www.vd.ch/toutes-les-actualites/hotline-et-informations-sur-le-coronavirus/point-de-situation-statistique-dans-le-canton-de-vaud/
    # includes a content from datawrapper ( https://datawrapper.dwcdn.net/tr5bJ/14/ ),
    # which provides actual data and table rendering.
    # Here we instead use datawrapper API directly to fetch the data.
    main_url = 'https://www.vd.ch/toutes-les-actualites/hotline-et-informations-sur-le-coronavirus/point-de-situation-statistique-dans-le-canton-de-vaud/'
    url = 'https://api.datawrapper.de/v3/charts/tr5bJ/data'
    print('Downloading:', main_url)
    # The bearer authentication token provided by Alex Robert ( https://github.com/AlexBobAlex )
    data = requests.get(url,
                        headers={'accept': 'text/csv',
                                 'Authorization': 'Bearer 6868e7b3be4d7a69eff00b1a434ea37af3dac1e76f32d9087fc544dbb3f4e229'})
    d = data.text

    # Date	Hospitalisations en cours	Dont soins intensifs	Sortis de l'hôpital	Décès	Total cas confirmés
    # 10.03.2020	36	8	5	1	130
    # 11.03.2020	38	7	5	3	200

    rows = d.split('\n')

    # Remove empty rows
    rows = [row for row in rows if len(row.strip())]

    headers = rows[0].split('\t')
    assert headers[0:6] == ["Date", "Hospitalisations en cours", "Dont soins intensifs", "Sortis de l'hôpital", "Décès", "Total cas confirmés"], f"Table header mismatch: Got: {headers}"

    is_first = True
    for row in rows:
        if not is_first:
            print('-' * 10)
        is_first = False

        cells = row.split('\t')
        print('VD')
        sc.timestamp()
        print('Downloading:', main_url)
        print('Date and time:', cells[0])
        print('Confirmed cases:', cells[5])
        print('Deaths:', cells[4])
        print('Hospitalized:', cells[1])
        print('ICU:', cells[2])
        if cells[3].isnumeric():
            print('Recovered:', cells[3])


def parse_xlsx():
    html_url = 'https://www.vd.ch/toutes-les-actualites/hotline-et-informations-sur-le-coronavirus/point-de-situation-statistique-dans-le-canton-de-vaud/'
    d = sc.download(html_url, silent=True)
    soup = BeautifulSoup(d, 'html.parser')
    xls_url = soup.find('a', string=re.compile("les donn.*es", flags=re.I)).get('href')
    assert xls_url, "URL is empty"
    xls = sc.xlsdownload(xls_url, silent=True)
    rows = [row for row in sc.parse_xls(xls, header_row=2) if isinstance(row['Date'], datetime.datetime)]
    is_first = True
    for row in sorted(rows, key=lambda row: row['Date'].date().isoformat()):
        if not is_first:
            print('-' * 10)
        is_first = False

        print('VD')
        sc.timestamp()
        print('Downloading:', html_url)
        print('Date and time:', row['Date'].date().isoformat())
        print('Confirmed cases:', row['Nombre total de cas confirmés positifs'])
        print('Hospitalized:', row['Hospitalisation en cours'])
        print('ICU:', row['Dont soins intensifs'])
        print('Deaths:', row['Décès parmi cas confirmés'])


def text_to_int(text):
    return int(re.sub('[^0-9]', '', text))


def parse_weekly_pdf():
    pdf_url = svc.get_weekly_pdf_url()
    pdf = sc.pdfdownload(pdf_url, silent=True)

    dd = sc.DayData(canton='VD', url=pdf_url)
    res = re.findall('Situation\s+au\s+(\d+\s+\w+\s+\d{4})', pdf, re.MULTILINE | re.DOTALL)
    if len(res) == 1:
        dd.datetime = res[0]
    dd.datetime = dd.datetime.replace('\n', ' ')
    if dd.datetime is None:
        dd.datetime = sc.find('Point .pid.miologique au (\d+\.\d+\.\d{4})', pdf)
    #dd.cases = text_to_int(sc.find('\s(\d+.\d+)\s+personnes ont .t. d.clar.es positives au SARS-CoV-2.', pdf))
    dd.hospitalized = sc.find('(\d+)\s+patients\s+(COVID-19\s+)?sont\s+(actuellement\s+)?hospitalis.s', pdf)
    dd.icu = sc.find('dont\s+(\d+)\s+en\s+soins\s+intensifs', pdf)
    assert dd
    print(dd)
    print('-' * 10)


if __name__ == '__main__':
    parse_weekly_pdf()
    # parse_xlsx()
