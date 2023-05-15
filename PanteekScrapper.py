import re
import requests
from bs4 import BeautifulSoup
from os.path import basename
import os
import time
from pathlib import Path
import logging

panteek = "https://www.panteek.com/"
#logging.basicConfig(filename='logfile.log', level=logging.INFO)


def main():
    #logging.info('soup for me')
    log = open('logs.txt', 'w')
    print('entering the matrix')
    site = requests.get(panteek)
    soup = BeautifulSoup(site.content, "html.parser")
    # finds p that contains the links
    row = soup.find('p', attrs = {'style': "border: solid green 1px; background-color: #ffffff; width: 190px"})
    urls = row.find_all('a')
    Path('prints').mkdir(parents=True, exist_ok=True)

    urList = []
    pageList = []
    # create list of dirs as well as each file
    for i in range(23):

        if i != 1:
            stripUrl = re.search('[^\/]*', urls[i].get('href'))
            if stripUrl.group(0).endswith('.htm'):
                Path('prints/' + stripUrl.group(0)[:-4]).mkdir(parents=True, exist_ok=True)
                pageList.append(stripUrl.group(0)[:-4])
            elif stripUrl.group(0).endswith('.html'):
                Path('prints/' + stripUrl.group(0)[:-5]).mkdir(parents=True, exist_ok=True)
                pageList.append(stripUrl.group(0)[:-5])
            else:
                Path('prints/' + stripUrl.group(0)).mkdir(parents=True, exist_ok=True)
                pageList.append(stripUrl.group(0))
            urList.append(panteek + urls[i].get('href'))
    try:  # main categories
        for li in urList[3:]:  # change to not get already collected pages
            try:
                pageList = pageList[3:]  # this one too
                newSite = requests.get(li)
                testSoup = BeautifulSoup(newSite.content, "html.parser")
                table = testSoup.find('table', id='main_table')
                if table == None:
                    pie = testSoup.find('table', {'cellspacing': '4'})
                    print('table == none found')
                    table = pie
                rows = table.find_all('tr')
                count = 0
                temp = testSoup.find('a', {'href': 'VitruviusBargain/index.htm'})
                for col in rows:  # artists in each row of table
                    try:
                        items = col.find_all('a')
                        time.sleep(3)
                        for url in items:  # each artist
                            print(url.get('href'))
                            printSite = requests.get(panteek + url.get('href'))
                            printSoup = BeautifulSoup(printSite.content, "html.parser")

                            # creates each artist's folder
                            stripName = re.search("(.+?)\/", url.get('href'))
                            Path('prints/' + pageList[count] + '/' + stripName.group(0)).mkdir(parents=True, exist_ok=True)
                            Path('prints/' + pageList[count] + '/' + stripName.group(0) + 'full_image').mkdir(parents=True,
                                                                                                              exist_ok=True)
                            Path('prints/' + pageList[count] + '/' + stripName.group(0) + 'thumb').mkdir(parents=True,
                                                                                                         exist_ok=True)

                            # for pages that lead to more pages
                            # if printSoup.find('style', attrs = {'background-image'}):
                            links = printSoup.find_all('a')
                            images = printSoup.find_all('img', border=0)
                            time.sleep(3)

                            # getting thumbnails
                            for thumb in images:
                                try:
                                    stripUrl = re.search('[^\/]*', url.get('href'))
                                    lnk = panteek + stripUrl.group(0) + '/' + thumb.get('src')
                                    path = 'prints/' + pageList[count] + '/' + stripName.group(0) + 'thumb'
                                    print(lnk)
                                    with open(os.path.join(path, basename(lnk)), "wb") as f:
                                        f.write(requests.get(lnk).content)
                                        f.close()
                                    time.sleep(3)
                                except (KeyError, IndexError):
                                    print("error in main thumb")
                            # getting main image
                            for link in links:
                                try:
                                    if link['href'].startswith('page'):
                                        stripUrl = re.search('[^\/]*', url.get('href'))
                                        lastSite = requests.get(panteek + stripUrl.group(0) + '/' + link['href'])
                                        lastSoup = BeautifulSoup(lastSite.content, "html.parser")
                                        limg = lastSoup.find_all('img')
                                        for bs in limg:
                                            #print(bs['src'])
                                            if bs['src'].startswith('../ima'):
                                                lnk = panteek + stripUrl.group(0) + limg[0].get('src')[2:]
                                                print(lnk)
                                                path = 'prints/' + pageList[count] + '/' + stripName.group(0) + 'full_image'
                                                with open(os.path.join(path, basename(lnk)), "wb") as f:
                                                    f.write(requests.get(lnk).content)
                                                    f.close()
                                                time.sleep(3)
                                except (KeyError, IndexError):
                                    print("error in main image")
                            nextPage = printSoup.find_all('font', attrs={'size': '4'})
                            if nextPage[1].text.startswith('Click for Page'):
                                pages = nextPage[1].find_all('a')
                                for page in pages:
                                    print(page.get('href'))
                                    if page.get('href').startswith('index'):
                                        reg = re.compile("(.+?)\/")
                                        toAdd = reg.findall(url.get('href'))
                                        print(panteek + toAdd[0] + '/' + page.get('href'))
                                        nPageUrl = requests.get(panteek + toAdd[0] + '/' + page.get('href'))
                                    else:
                                        nPageUrl = requests.get(panteek + page.get('href'))

                                    nPageSoup = BeautifulSoup(nPageUrl.content, "html.parser")
                                    links = nPageSoup.find_all('a')
                                    images = nPageSoup.find_all('img', border = 0)
                                    for thumb in images:
                                        try:
                                            stripUrl = re.search('[^\/]*', url.get('href'))
                                            lnk = panteek + stripUrl.group(0) + '/' + thumb.get('src')
                                            path = 'prints/' + pageList[count] + '/' + stripName.group(0) + 'thumb'
                                            print(lnk)
                                            with open(os.path.join(path, basename(lnk)), "wb") as f:
                                                f.write(requests.get(lnk).content)
                                                f.close()
                                            time.sleep(3)
                                        except (KeyError, IndexError):
                                            print("error in next page thumb")

                                    for link in links:
                                        try:
                                            if link['href'].startswith('page'):
                                                stripUrl = re.search('[^\/]*', url.get('href'))
                                                lastSite = requests.get(panteek + stripUrl.group(0) + '/' + link['href'])
                                                lastSoup = BeautifulSoup(lastSite.content, "html.parser")
                                                limg = lastSoup.find_all('img')
                                                lnk = panteek + stripUrl.group(0) + limg[0].get('src')[2:]
                                                print(lnk)
                                                path = 'prints/' + pageList[count] + '/' + stripName.group(0) + 'full_image'
                                                with open(os.path.join(path, basename(lnk)), "wb") as f:
                                                    f.write(requests.get(lnk).content)
                                                    f.close()
                                                time.sleep(3)
                                        except (KeyError, IndexError):
                                            print("error in next page main image")
                                time.sleep(1)
                    except (AttributeError, IndexError):
                        print('error col ')
                count += 1
            except AttributeError:
                print("row error")
    except (KeyError, ConnectionError):
        print("error li")
    log.close()


if __name__ == '__main__':
    main()
