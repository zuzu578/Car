import random
import string
import time

import urllib3
from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

CHARACTERS = (
        string.ascii_letters
        + string.digits
)

def bobaeCrawling(db):
    crowlingCnt = 0
    itemNum = 0

    cursor = db.cursor()
    selectSql1 = """SELECT ITEM_NUM FROM CAR_DATA WHERE SITE = '보배드림' ORDER BY ITEM_NUM DESC"""
    cursor.execute(selectSql1)
    data = cursor.fetchall()

    if data is not None and len(data) > 0:
        row = data[0]
        itemNum = row[0]

    while crowlingCnt < 100000:
        try:
            carData = {}

            crowlingNum = itemNum+crowlingCnt
            url = 'https://www.bobaedream.co.kr/mycar/mycar_view.php?no='+str(crowlingNum)+'&gubun=K'

            carData["url"] = url
            print(url)

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # session = requests.Session()
            # retry = Retry(connect=3, backoff_factor=0.5)
            # adapter = HTTPAdapter(max_retries=retry)
            # session.mount('http://', adapter)
            # session.mount('https://', adapter)

            # req = session.get(url)

            req = requests.get(url, verify=False)

            soup = BeautifulSoup(req.content.decode('utf-8', 'replace'), 'lxml')

            # print(soup)

            groupInfo = soup.find('div', attrs={'class': 'group-info'})

            if groupInfo is not None:
                priceDiv = groupInfo.find('div', attrs={'class': 'price-area'})
                price = priceDiv.find('span', attrs={'class': 'price'}).getText()
                if price.find('판매완료') != -1:
                    crowlingCnt = crowlingCnt + 1

                    continue
                else:
                    findPrice(price, carData)
                    findTitle(groupInfo, carData)
                    findLocation(groupInfo, carData)
                    findCarNum(soup, carData)
                    findDetail(soup,carData)
                    findImageList(soup, carData, db)


                    if len(carData) > 1:
                        try:
                            with db.cursor() as cursor:
                                sql = 'INSERT INTO CAR_DATA (LINK_URL, TITLE ,BRAND, MODEL, CAR_NUM, PRICE, CAR_YEAR, OIL_TYPE, GEAR_TYPE, COLOR, VEHICLEMILE, LOCATION, IMAGE_ID,CAR_VIEWS,SITE,ITEM_NUM) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)'
                                cursor.execute(sql, (
                                    carData["url"], carData["title"], carData["brand"], carData["model"], carData["carNum"],
                                    carData["price"], carData["year"], carData["oilType"], carData["gearType"],
                                    carData["color"], carData["vehicleMile"], carData["location"], carData["uniqueKey"], 0,
                                    '보배드림',
                                    itemNum))
                            db.commit()
                            print('success >>>' + str(itemNum))
                        except Exception as ex:
                            print('db error >>>' + str(ex))
        except Exception as ex:
            print("Exception >>> " + str(ex))

        crowlingCnt = crowlingCnt+1
        print()
        time.sleep(1)

def findTitle(groupInfo,carData):
    titleArea = groupInfo.find('div', attrs={'class': 'title-area'})
    title = titleArea.find('h3').getText()
    carData["title"] = title.replace('\xa0','')
    # print(title)

    if title is not None:
        # 브랜드
        brandAndModelSplit = title.split()
        brand = brandAndModelSplit[0]
        carData["brand"] = brand
        # print(brand)

        # 모델
        model = title.replace(brand + ' ', '')
        if model[0:1] == ' ':
            model = model[1:len(model)]
        carData["model"] = model
        # print(model)

def findPrice(price,carData):
    if price.find('가격상담') != -1:
        price = '0'
    else:
        price = price.replace('만원', '').replace(',', '')

    carData["price"] = int(price)
    # print(price)


def findLocation(groupInfo,carData):
    sellerInfo = groupInfo.find('div', attrs={'class': 'seller-info'})
    seller = sellerInfo.getText().replace('\n', '').replace('\r', '').strip()

    location = "기타"

    if seller.find('서울') != -1:
        location = "서울"
    elif seller.find('인천') != -1:
        location = "인천"
    elif seller.find('대전') != -1:
        location = "대전"
    elif seller.find('대구') != -1:
        location = "대구"
    elif seller.find('부산') != -1:
        location = "부산"
    elif seller.find('광주') != -1:
        location = "광주"
    elif seller.find('울산') != -1:
        location = "울산"
    elif seller.find('충남') != -1:
        location = "충남"
    elif seller.find('충북') != -1:
        location = "충북"
    elif seller.find('전남') != -1:
        location = "전남"
    elif seller.find('전북') != -1:
        location = "전북"
    elif seller.find('경북') != -1:
        location = "경북"
    elif seller.find('경남') != -1:
        location = "경남"
    elif seller.find('강원') != -1:
        location = "강원"
    elif seller.find('경기') != -1:
        location = "경기"
    carData["location"] = location
    # print(location)

def findCarNum(soup,carData):
    galleryData = soup.find('div', attrs={'class': 'gallery-data'})
    carNum = galleryData.find('dd', attrs={'class': 'txt-bar'}).getText()
    carNum = carNum.replace('차량번호 ','')
    carNum = carNum.replace(':', '')
    carData["carNum"] = carNum
    # print(carNum)

def findDetail(soup,carData):
    detailDiv = soup.find('div', attrs={'class': 'info-basic'})

    if detailDiv is not None:
        table = detailDiv.find('table')
        tag_body = table.find('tbody')

        year = 0
        oilType = ""
        changeGearType = ""
        color = ""
        vehicleMile = 0

        tdsCount = 0
        for td in tag_body.findAll('td'):
            td = str(td)
            td = td.replace('<td colspan="3">', '').replace('<td>', '').replace('</td>', '').replace('&nbsp;','').replace(u'\xa0', u'')
            if tdsCount == 0:
                end = td.find('.')
                yearString = td[0:end].replace(' ', '').replace('년', '')
                if yearString != '':
                    year = int(yearString)
                # print(year)
            elif tdsCount == 2:
                vehicleMileSting = td.replace(',', '').replace('km', '')
                if vehicleMileSting != '':
                    vehicleMile = int(vehicleMileSting)
                # print(vehicleMile)
            elif tdsCount == 3:
                color = td
                # print(color)
            elif tdsCount == 4:
                changeGearType = td
                # print(changeGearType)
            elif tdsCount == 6:
                oilType = td
                # print(oilType)

            tdsCount = tdsCount + 1

        carData["year"] = year
        carData["oilType"] = oilType
        carData["gearType"] = changeGearType
        carData["color"] = color
        carData["vehicleMile"] = vehicleMile


def findImageList(soup,carData,db):
    imageList = soup.find('div', attrs={'class': 'gallery-thumb js-gallery-thumb'})
    uniqueKey = generate_unique_key()
    carData["uniqueKey"] = uniqueKey

    for aTag in imageList.findAll('a'):
        if aTag is not None:
            img = aTag.find('img')
            if img is not None:
                imgUrl = img['src']

                try:
                    with db.cursor() as cursor:
                        sql = 'INSERT INTO IMAGE_LIST (IMG_ID, IMG_URL) VALUES (%s, %s)'
                        cursor.execute(sql, (uniqueKey,imgUrl))
                finally:
                    None

def generate_unique_key():
    return ''.join(random.sample(CHARACTERS, 15))