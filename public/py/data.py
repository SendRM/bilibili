import requests
from bs4 import BeautifulSoup
import csv
import re

def getContent(url):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
    res = requests.get(url = url, headers = header)
    content = BeautifulSoup(res.content, "html5lib")
    return content

def classFind(con, ele, className, other = None):
    findCon = con.find(ele, attrs={"class": className})
    if other:
        findCon = findCon.find(other)
    return findCon


url = "https://www.bilibili.com/"
content = getContent(url)
links = content.find_all("a", attrs={"class": "channel-link"})
# links = links[0 : len(links) - 11]
links = links[0 : 6]
frontUrl = "https://api.bilibili.com/pgc/season/index/result?"
api = {
    "anime": "season_version=-1&spoken_language_type=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=20&type=1",
    "movie": "st=2&order=2&area=-1&style_id=-1&release_date=-1&season_status=-1&sort=0&page=1&season_type=2&pagesize=20&type=1",
    "guochuang": "season_version=-1&is_finish=-1&copyright=-1&season_status=-1&year=-1&style_id=-1&order=3&st=4&sort=0&page=1&season_type=4&pagesize=20&type=1",
    "tv": "st=5&order=2&area=-1&style_id=-1&release_date=-1&season_status=-1&sort=0&page=1&season_type=5&pagesize=20&type=1",
    "variety": "st=7&order=2&season_status=-1&style_id=-1&sort=0&page=1&season_type=7&pagesize=20&type=1",
    "documentary": "st=3&order=2&style_id=-1&producer_id=-1&release_date=-1&season_status=-1&sort=0&page=1&season_type=3&pagesize=20&type=1"
}
for i in links:
    link = "https:" + i.get("href")
    href = link.split('/')
    key = href[len(href) - 1]
    if (key == '' or key == ' '):
        key = href[len(href) - 2]
    category = key + '.csv'
    if api[key]:
        with open(category, "a", encoding="utf-8", newline="") as f:
            f = csv.writer(f)
            head = ["name", "play", "fans", "label", "score", "times", "date", "info", "imgUrl", "longComments", "shortComments"]
            f.writerow(head)
        res = requests.get(frontUrl + api[key]).json()['data']
        num = res['total'] // 20 + 2
        for i in range(1, num):
                index1 = api[key].find('page=') + 5
                index2 = api[key].find('&season_type')
                api[key] = api[key][0: index1] + str(i) + api[key][index2:]
                res = requests.get(frontUrl + api[key]).json()['data']
                try:
                    for j in res['list']:
                        try:
                            url = "https:" + getContent(j['link']).find("a", attrs={"class": "media-title"}).get("href")
                        except AttributeError as e:
                            url = "https:" + getContent(j['link']).find("a", attrs={"class": "media-title"}).get("href")
                        finally:
                            con = getContent(url)
                            name = j["title"]
                            play = classFind(con, "span", "media-info-count-item-play", "em").text
                            fans = j['order']
                            label = classFind(con, "span", "media-info-count-item-review", "em").text
                            score = j['score']
                            times = classFind(con, "div", "media-info-review-times").text if classFind(con, "div",
                                                                                                       "media-info-review-times") else ""
                            date = classFind(con, "div", "media-info-time").find_all("span")[0].text
                            info = classFind(con, "div", "media-info-time").find_all("span")[1].text
                            imgUrl = j['cover']
                            box = classFind(con, "div", "media-tab-nav").find_all("li")
                            longComments = ""
                            shortComments = ""
                            if len(box) > 1:
                                if len(box[1].text) > 2:
                                    longComments = re.sub('\D', "", box[1].text)
                                if len(box[2].text) > 2:
                                    shortComments = re.sub('\D', "", box[2].text)
                            print("当前爬取页码:", i, name)
                            with open(category, "a", encoding="utf-8", newline="") as file:
                                csv.writer(file).writerow(
                                    [name, play, fans, label, score, times, date, info, imgUrl, longComments,
                                     shortComments])
                except KeyError as e:
                    continue