import random
import string
import time

import requests
from bs4 import BeautifulSoup

CHARACTERS = (
        string.ascii_letters
        + string.digits
)


def encarCrawling(db):
    crowlingCnt = 0
    itemNum = 0

    cursor = db.cursor()
    selectSql1 = """SELECT ITEM_NUM FROM CAR_DATA WHERE SITE = 'SK엔카' ORDER BY ITEM_NUM DESC"""
    cursor.execute(selectSql1)
    data = cursor.fetchall()

    if data is not None and len(data) > 0:
        row = data[0]
        itemNum = row[0]

    while crowlingCnt < 100000:
        try:
            carData = {}

            crowlingNum = itemNum + crowlingCnt
            url = 'http://www.encar.com/dc/dc_cardetailview.do?carid=' + str(crowlingNum)

            carData["url"] = url
            print(url)

            req = requests.get(url)

            soup = BeautifulSoup(req.content.decode('euc-kr', 'replace'), 'lxml')

            productFloating = soup.find('div', attrs={'class': 'product_floating'})

            if productFloating is not None:
                ass = soup.find('em', attrs={'class': 'ass'})
                if ass is not None:
                    asForm(soup,carData,db)
                else:
                    nomalForm(soup,carData,db)

                # print(carData)
                if len(carData) > 1:
                    try:
                        with db.cursor() as cursor:
                            sql = 'INSERT INTO CAR_DATA (LINK_URL, TITLE ,BRAND, MODEL, CAR_NUM, PRICE, CAR_YEAR, OIL_TYPE, GEAR_TYPE, COLOR, VEHICLEMILE, LOCATION, IMAGE_ID,CAR_VIEWS,SITE,ITEM_NUM) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)'
                            cursor.execute(sql, (
                                carData["url"], carData["title"], carData["brand"], carData["model"], carData["carNum"],
                                carData["price"], carData["year"], carData["oilType"], carData["gearType"],
                                carData["color"], carData["vehicleMile"], carData["location"], carData["uniqueKey"], 0,
                                'SK엔카',
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


def nomalForm(soup,carData,db):
    productLeft = soup.find('div', attrs={'class': 'product_left'})
    info = productLeft.find('div', attrs={'class': 'area_info'})
    if info is not None:
        # 타이틀
        findTitle(info, carData)
        # 가격
        findPrice(info, carData)
        # 상세
        findDetail(info, carData)
        # 주소
        findLocation(soup, carData)
        # 이미지
        imageList = productLeft.find('div', attrs={'class': 'gallery_thumbnail'})
        if imageList is not None:
            findImageList(imageList, carData, db)

def asForm(soup,carData,db):
    areaImage = soup.find('div', attrs={'class': 'area_image'})
    info = areaImage.find('div', attrs={'class': 'info_product'})
    if info is not None:
        # 타이틀
        findASTitle(info,carData)
        # 가격
        findASPrice(areaImage,carData)
        # 상세
        findASDetail(info, carData)
        # 주소
        findASLocation(soup, carData)
        # 이미지
        imageList = areaImage.find('div', attrs={'class': 'gallery_thumbnail'})
        if imageList is not None:
            findImageList(imageList, carData, db)




def findTitle(info,carData):

    title = info.find('h1')
    carData["title"] = title.getText()
    # print(title)

    if title is not None:
        brandAndModel = title.find('span', attrs={'class': 'brand'}).getText()

        # 브랜드
        brandAndModelSplit = brandAndModel.split()
        brand = brandAndModelSplit[0]
        carData["brand"] = brand
        # print(brand)

        # 모델
        model = brandAndModel.replace(brand + ' ', '')

        if model[0:1] == ' ':
            model = model[1:len(model)]

        carData["model"] = model
        # print(model)

        detail = title.find('span', attrs={'class': 'detail'})

def findPrice(info,carData):
    priceDiv = info.find('div', attrs={'class': 'prod_price'})
    price = priceDiv.find('span', attrs={'class': 'num'}).getText()
    price = price.replace('만원', '').replace(',', '')
    carData["price"] = int(price)
    # print(price)


def findDetail(info,carData):
    detailDiv = info.find('div', attrs={'class': 'prod_infomain'})

    if detailDiv is not None:
        for li in detailDiv.findAll('li'):
            item = li.getText().replace(' ', '').replace('\n', '').replace('\r', '').strip()

            if item.find('주행거리') != -1:
                item = item.replace('주행거리:', '').replace(',', '').replace('Km', '')
                carData["vehicleMile"] = int(item)
            elif item.find('연식') != -1:
                item = item.replace('연식:', '').replace('자세히보기', '')
                year = "20"+item[0:2]
                carData["year"] = int(year)
            elif item.find('연료') != -1:
                item = item.replace('연료:', '')
                carData["oilType"] = item
            elif item.find('차종') != -1:
                item = item.replace('차종:', '')
            elif item.find('배기량') != -1:
                item = item.replace('배기량:', '')
            elif item.find('변속기') != -1:
                item = item.replace('변속기:', '')
                carData["gearType"] = item
            elif item.find('색상') != -1:
                item = item.replace('색상:', '')
                carData["color"] = item
            elif item.find('차량번호') != -1:
                item = item.replace('차량번호', '')
                carData["carNum"] = item.replace(':','')

            # print(item)

def findLocation(soup,carData):
    productRight = soup.find('div', attrs={'class': 'product_right'})
    addrDiv = productRight.find('div',attrs={'class': 'addr'})
    addr = addrDiv.find('a').getText()

    location = "기타"

    if addr.find('서울') != -1:
        location = "서울"
    elif addr.find('인천') != -1:
        location = "인천"
    elif addr.find('대전') != -1:
        location = "대전"
    elif addr.find('대구') != -1:
        location = "대구"
    elif addr.find('부산') != -1:
        location = "부산"
    elif addr.find('광주') != -1:
        location = "광주"
    elif addr.find('울산') != -1:
        location = "울산"
    elif addr.find('충남') != -1:
        location = "충남"
    elif addr.find('충북') != -1:
        location = "충북"
    elif addr.find('전남') != -1:
        location = "전남"
    elif addr.find('전북') != -1:
        location = "전북"
    elif addr.find('경북') != -1:
        location = "경북"
    elif addr.find('경남') != -1:
        location = "경남"
    elif addr.find('강원') != -1:
        location = "강원"
    elif addr.find('경기') != -1:
        location = "경기"
    carData["location"] = location


def findImageList(imageList,carData,db):
    ul = imageList.find('ul')

    uniqueKey = generate_unique_key()
    carData["uniqueKey"] = uniqueKey
    if ul is not None:

        for li in ul.findAll('li'):
            if li is not None:
                aTag = li.find('a')
                if aTag is not None:
                    img = aTag.find('img')
                    if img is not None:
                        imgUrl = img['src']
                        imgUrlEnd = imgUrl.find('?')

                        if imgUrlEnd != -1:
                            imgUrl = imgUrl[0:imgUrlEnd]

                        try:
                            with db.cursor() as cursor:
                                sql = 'INSERT INTO IMAGE_LIST (IMG_ID, IMG_URL) VALUES (%s, %s)'
                                cursor.execute(sql, (uniqueKey,imgUrl))
                        finally:
                            None


def findASTitle(info,carData):

    title = info.find('strong',attrs={'class': 'prod_name'})
    carData["title"] = title.getText()
    # print(title)

    if title is not None:
        brandAndModel = title.find('span', attrs={'class': 'brand'}).getText()

        # 브랜드
        brandAndModelSplit = brandAndModel.split()
        brand = brandAndModelSplit[0]
        carData["brand"] = brand
        # print(brand)

        # 모델
        model = brandAndModel.replace(brand + ' ', '')

        if model[0:1] == ' ':
            model = model[1:len(model)]

        carData["model"] = model
        # print(model)

        detail = title.find('span', attrs={'class': 'detail'})

def findASPrice(areaImage,carData):
    priceEm = areaImage.find('em', attrs={'class': 'emph_price'})
    price = priceEm.find('span', attrs={'class': 'txt_num'}).getText()
    price = price.replace('만원', '').replace(',', '')
    carData["price"] = int(price)
    # print(price)


def findASDetail(info,carData):
    detail = info.find('ul', attrs={'class': 'list_carinfo'})

    if detail is not None:
        for li in detail.findAll('li'):
            item = li.getText().replace(' ', '').replace('\n', '').replace('\r', '').strip()

            if item.find('주행거리') != -1:
                item = item.replace('주행거리:', '').replace(',', '').replace('Km', '')
                carData["vehicleMile"] = int(item)
            elif item.find('연식') != -1:
                item = item.replace('연식:', '').replace('자세히보기', '')
                year = "20"+item[0:2]
                carData["year"] = int(year)
            elif item.find('연료') != -1:
                item = item.replace('연료:', '')
                carData["oilType"] = item
            elif item.find('차종') != -1:
                item = item.replace('차종:', '')
            elif item.find('배기량') != -1:
                item = item.replace('배기량:', '')
            elif item.find('변속기') != -1:
                item = item.replace('변속기:', '')
                carData["gearType"] = item
            elif item.find('색상') != -1:
                item = item.replace('색상:', '')
                carData["color"] = item
            elif item.find('차량번호') != -1:
                item = item.replace('차량번호', '')
                carData["carNum"] = item

            # print(item)

def findASLocation(soup,carData):
    detailSeller = soup.find('div', attrs={'class': 'detail_seller'})
    addr = detailSeller.find('a',attrs={'class': 'link_address'}).getText()
    location = "기타"

    if addr.find('서울') != -1:
        location = "서울"
    elif addr.find('인천') != -1:
        location = "인천"
    elif addr.find('대전') != -1:
        location = "대전"
    elif addr.find('대구') != -1:
        location = "대구"
    elif addr.find('부산') != -1:
        location = "부산"
    elif addr.find('광주') != -1:
        location = "광주"
    elif addr.find('울산') != -1:
        location = "울산"
    elif addr.find('충남') != -1:
        location = "충남"
    elif addr.find('충북') != -1:
        location = "충북"
    elif addr.find('전남') != -1:
        location = "전남"
    elif addr.find('전북') != -1:
        location = "전북"
    elif addr.find('경북') != -1:
        location = "경북"
    elif addr.find('경남') != -1:
        location = "경남"
    elif addr.find('강원') != -1:
        location = "강원"
    elif addr.find('경기') != -1:
        location = "경기"
    carData["location"] = location
    # print(location)


def findASImageList(imageList,carData,db):
    ul = imageList.find('ul')

    uniqueKey = generate_unique_key()
    carData["uniqueKey"] = uniqueKey
    if ul is not None:

        for li in ul.findAll('li'):
            if li is not None:
                aTag = li.find('a')
                if aTag is not None:
                    img = aTag.find('img')
                    if img is not None:
                        imgUrl = img['src']
                        imgUrlEnd = imgUrl.find('?')

                        if imgUrlEnd != -1:
                            imgUrl = imgUrl[0:imgUrlEnd]

                        try:
                            with db.cursor() as cursor:
                                sql = 'INSERT INTO IMAGE_LIST (IMG_ID, IMG_URL) VALUES (%s, %s)'
                                cursor.execute(sql, (uniqueKey,imgUrl))
                        finally:
                            None

def generate_unique_key():
    return ''.join(random.sample(CHARACTERS, 15))
