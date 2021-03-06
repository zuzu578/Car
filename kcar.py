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

def kcarCrawling(db):
    crowlingCnt = 0
    itemNum = 50000

    cursor = db.cursor()
    selectSql1 = """SELECT ITEM_NUM FROM CAR_DATA WHERE SITE = 'Kcar' ORDER BY ITEM_NUM DESC"""
    cursor.execute(selectSql1)
    data = cursor.fetchall()

    if data is not None and len(data) > 0:
        row = data[0]
        itemNum = row[0]

    while crowlingCnt < 100000:
        try:
            carData = {}

            crowlingNum = itemNum+crowlingCnt

            url = 'https://www.kcar.com/car/info/car_info_detail.do?i_sCarCd=EC'+str(crowlingNum)

            carData["url"] = url
            print(url)

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            #session = requests.Session()
            #retry = Retry(connect=3, backoff_factor=0.5)
            #adapter = HTTPAdapter(max_retries=retry)
            #session.mount('http://', adapter)
            #session.mount('https://', adapter)

            #req = session.get(url)

            req = requests.get(url, verify=False)

            soup = BeautifulSoup(req.content.decode('utf-8', 'replace'), 'lxml')

            # print(soup)

            groupInfo = soup.find('div', attrs={'class': 'car_detail_info'})

            if groupInfo is not None:
                title = groupInfo.find('h2').getText().replace('\n', '').replace('\r', '').replace('    ', '')

                if title is not None and title != '':

                    findTitle(title, carData)
                    findDetail(groupInfo,carData)
                    findPrice(groupInfo, carData)

                    carImgInfo = soup.find('div', attrs={'class': 'car_img_wrap'})
                    findCarNum(carImgInfo, carData)
                    findImageList(carImgInfo, carData, db)


                    if len(carData) > 1:
                        try:
                            with db.cursor() as cursor:
                                sql = 'INSERT INTO CAR_DATA (LINK_URL, TITLE ,BRAND, MODEL, CAR_NUM, PRICE, CAR_YEAR, OIL_TYPE, GEAR_TYPE, COLOR, VEHICLEMILE, LOCATION, IMAGE_ID,CAR_VIEWS,SITE,ITEM_NUM) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)'
                                cursor.execute(sql, (
                                    carData["url"], carData["title"], carData["brand"], carData["model"], carData["carNum"],
                                    carData["price"], carData["year"], carData["oilType"], carData["gearType"],
                                    carData["color"], carData["vehicleMile"], carData["location"], carData["uniqueKey"], 0,
                                    'Kcar',
                                    itemNum))
                            # db.commit()
                            print('success >>>' + str(itemNum))
                        except Exception as ex:
                            print('db error >>>' + str(ex))
        except Exception as ex:
            print("Exception >>> " + str(ex))

        crowlingCnt = crowlingCnt+1
        print()
        time.sleep(1)

def findTitle(title,carData):
    carData["title"] = title
    # print(title)

    if title is not None:
        # ?????????
        brandAndModelSplit = title.split()
        brand = brandAndModelSplit[0]
        carData["brand"] = brand
        # print(brand)

        # ??????
        model = title.replace(brand + ' ', '')
        if model[0:1] == ' ':
            model = model[1:len(model)]
        carData["model"] = model
        # print(model)

def findPrice(groupInfo,carData):
    priceInfo = groupInfo.find('div', attrs={'class': 'car_price_info'})

    if priceInfo is not None:

        if priceInfo.find('????????? ??????') != -1:
            delPrice = priceInfo.find('del')
            if delPrice is not None or delPrice != -1:
                price = delPrice.getText().replace('??????', '').replace(',', '')
            else:
                price = '0'
        else:
            priceInfo = priceInfo.getText().replace('\n', '').replace('\r', '').replace('\t', '')
            start = priceInfo.find('?????????')
            if start != -1:
                priceInfo[start:len(priceInfo)]
                price = priceInfo.replace('??????', '').replace(',', '')
            else:
                price ='0'
    else:
        price = '0'

    carData["price"] = int(price)
    # print(price)


def findLocation(groupInfo,carData):
    sellerInfo = groupInfo.find('div', attrs={'class': 'seller-info'})
    seller = sellerInfo.getText().replace('\n', '').replace('\r', '').strip()

    location = "??????"

    if seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    elif seller.find('??????') != -1:
        location = "??????"
    carData["location"] = location
    # print(location)

def findCarNum(carImgInfo,carData):
    carNumInfo = carImgInfo.find('span', attrs={'class': 'valuator'})
    carNum = carNumInfo.find('i').getText()
    carData["carNum"] = carNum
    # print(carNum)

def findDetail(groupInfo,carData):
    detailDiv = groupInfo.find('div', attrs={'class': 'car_desc'})

    if detailDiv is not None:

        year = 0
        oilType = ""
        changeGearType = ""
        color = ""
        vehicleMile = 0

        spanCount = 0
        for span in detailDiv.findAll('span'):
            span = span.getText().replace('\n', '').replace('\r', '').replace('\t', '').replace('   ', '')
            if spanCount == 1:
                end = span.find('???')
                yearString = span[0:end].replace('???', '')
                if len(yearString) == 2:
                    yearString = '20'+ yearString

                if yearString != '':
                    year = int(yearString)
                print(year)
            elif spanCount == 2:
                vehicleMileSting = span.replace(',', '').replace('km', '')
                if vehicleMileSting != '':
                    vehicleMile = int(vehicleMileSting)
                print(vehicleMile)
            elif spanCount == 3:
                oilType = span
                print(oilType)
            elif spanCount == 4:
                color = span
                print(color)
            elif spanCount == 5:
                changeGearType = span
                print(changeGearType)
            elif spanCount == 6:
                location = span
                print(location)

            spanCount = spanCount + 1

        carData["year"] = year
        carData["oilType"] = oilType
        carData["gearType"] = changeGearType
        carData["color"] = color
        carData["vehicleMile"] = vehicleMile
        carData["location"] = location


def findImageList(soup,carData,db):
    imageList = soup.find('div', attrs={'class': 'bx_thumb'})
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