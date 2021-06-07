import random
import string
import time

import requests
from bs4 import BeautifulSoup

CHARACTERS = (
        string.ascii_letters
        + string.digits
)

def kuCrawling(db):
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
        # print(crowlingCnt)
        # subCrowlingCnt = 0
        # while subCrowlingCnt < 5000:
            try:
                carData = {}
                crowlingNum = itemNum + crowlingCnt


                # db 조회
                # with db.cursor() as cursor:
                #     sql = "select ITEM_NUM from CAR_DATA where ITEM_NUM = %s"
                #     cursor.execute(sql,(itemNum))
                #     rows = cursor.fetchone()
                #     if rows is not None and len(rows) > 0:
                #         print(rows[0])

                url = 'http://www.carku.kr/search/car-detail.asp?wDemoNo=0' + str(crowlingNum)

                carData["url"] = url

                print(url)

                req = requests.get(url)
                soup = BeautifulSoup(req.content.decode('euc-kr','replace'),'lxml')

                carDetailDiv = soup.find('div', attrs={'class': 'car-detail'})
                if carDetailDiv is not None:

                    findTitle(carDetailDiv,carData)

                    if carData['title'] == '기타':
                        print(str(itemNum) + '- 기타')
                    else:
                        findPriceAndCarNum(carDetailDiv,carData)
                        findDetail(carDetailDiv,carData)
                        findImageList(carDetailDiv, carData, db)

                        # print(carData)

                        if len(carData) > 1:
                            try:
                                with db.cursor() as cursor:
                                    sql = 'INSERT INTO CAR_DATA (LINK_URL, TITLE ,BRAND, MODEL, CAR_NUM, PRICE, CAR_YEAR, OIL_TYPE, GEAR_TYPE, COLOR, VEHICLEMILE, LOCATION, IMAGE_ID,CAR_VIEWS,SITE,ITEM_NUM) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)'
                                    cursor.execute(sql, (carData['url'], carData['title'], carData['brand'], carData['model'], carData['carNum'], carData['price'], carData['year'], carData['oilType'], carData['gearType'], carData['color'], carData['vehicleMile'], carData['location'],carData['uniqueKey'], 0,'전국자동차매매사업조합연합회',itemNum))
                                db.commit()
                                print('success >>>' +str(itemNum))
                            except Exception as ex:
                                print('db error >>>'+str(ex))
            except Exception as ex:
                print("Exception >>> " + str(ex))
            # subCrowlingCnt = subCrowlingCnt + 1

            crowlingCnt = crowlingCnt + 1
            print()
            time.sleep(1)



def findTitle(carDetailDiv,carData):
    title = carDetailDiv.find('h3')
    # print(title)
    titleString = str(title).replace('amp;', '')
    titleString = titleString.replace('<h3>', '').replace('</h3>', '')
    titleString = titleString.replace('&nbsp;', '')
    titleString = titleString.replace(u'\xa0', u'')

    # carData.append(titleString)
    carData["title"] = titleString

    if titleString.find("[") != -1:
        brandStart = titleString.find("[")+1
        brandEnd = titleString.find("]")
        brand = titleString[brandStart:brandEnd]
        # print(brand)
        # carData.append(brand)
        carData["brand"] = brand

        subtitle = titleString[brandEnd+1:len(titleString)]

        modelEnd = subtitle.find('(') - 1
        if modelEnd == -2:
            model = subtitle[0:len(subtitle)]
        else:
            if subtitle.find('(신형)') != -1:
                model = subtitle[0:subtitle.find('(신형)')+4]
            else:
                model = subtitle[0:modelEnd]

        # print(model)
        # carData.append(model)
        if model[0:1] == ' ':
            model = model[1:len(model)]
        carData["model"] = model

def findPriceAndCarNum(carDetailDiv,carData):
    table = carDetailDiv.find('table', attrs={'class': 'detail1'})
    # print(table)
    tag_body = table.find('tbody')
    price = 0
    carNum = ""

    for tr in tag_body.findAll('tr'):
        ths = tr.findAll('th')
        for th in ths:
            if(th is not None):
                thString = str(th)
                thString = thString.replace('&nbsp;', '')
                thString = thString.replace(u'\xa0', u'')
                if '판매가' in thString:
                    start = thString.find('<span class="red">') + 18
                    end = thString.find('</span>')
                    priceString = thString[start:end]
                    priceString = priceString.replace('만원','').replace(',','').replace('상담','')

                    if priceString != '':
                        price = int(priceString)

                    # print(price)
                elif'차량번호' in thString:
                    start = thString.find('<span class="red">') + 18
                    end = thString.find('</span>')
                    carNum = thString[start:end]
                    # print(carNum)
                    carNum = carNum.replace(':','')

    # carData.append(carNum)
    # carData.append(price)
    carData["carNum"] = carNum
    carData["price"] = price

def findDetail(carDetailDiv,carData):
    table = carDetailDiv.find('table', attrs={'class': 'detail2'})
    tag_body = table.find('tbody')

    year = 0
    oilType = ""
    changeGearType = ""
    color = ""
    vehicleMile = 0
    location = ""

    tdsCount = 0
    for tr in tag_body.findAll('tr'):
        tds = tr.findAll('td')

        for td in tds:
            td = str(td)
            td = td.replace('<td colspan="3">','').replace('<td>','').replace('</td>','').replace('&nbsp;', '').replace(u'\xa0', u'')
            if tdsCount == 0:
                end = td.find('|')
                yearString = td[0:end].replace(' ','').replace('년','')
                if yearString != '':
                    year = int(yearString)
                # print(year)
            elif tdsCount == 1:
                oilType = td
                # print(oilType)
            elif tdsCount == 2:
                changeGearType = td
                # print(changeGearType)
            elif tdsCount == 3:
                color = td
                # print(color)
            elif tdsCount == 4:
                vehicleMileSting = td.replace(',','').replace('km','')
                if vehicleMileSting != '':
                    vehicleMile = int(vehicleMileSting)
                # print(vehicleMile)
            else :
                if td.find('서울') != -1:
                    location = "서울"
                elif td.find('인천') != -1:
                    location = "인천"
                elif td.find('대전') != -1:
                    location = "대전"
                elif td.find('대구') != -1:
                    location = "대구"
                elif td.find('부산') != -1:
                    location = "부산"
                elif td.find('광주') != -1:
                    location = "광주"
                elif td.find('울산') != -1:
                    location = "울산"
                elif td.find('충남') != -1 or td.find('충청남도') != -1:
                    location = "충남"
                elif td.find('충북') != -1 or td.find('충청북도') != -1:
                    location = "충북"
                elif td.find('전남') != -1 or td.find('전라남도') != -1:
                    location = "전남"
                elif td.find('전북') != -1 or td.find('전라북도') != -1:
                    location = "전북"
                elif td.find('경북') != -1 or td.find('경상북도') != -1:
                    location = "경북"
                elif td.find('경남') != -1 or td.find('경상남도') != -1:
                    location = "경남"
                elif td.find('강원') != -1:
                    location = "강원"
                elif td.find('경기') != -1:
                    location = "경기"


            tdsCount = tdsCount + 1

    carData["year"] = year
    carData["oilType"] = oilType
    carData["gearType"] = changeGearType
    carData["color"] = color
    carData["vehicleMile"] = vehicleMile
    carData["location"] = location



def findImageList(carDetailDiv,carData,db):
    imageList = carDetailDiv.find('div', attrs={'class': 's_img'})
    # print(imageList)
    ul = imageList.find('ul')

    uniqueKey = generate_unique_key()
    # carData.append(uniqueKey)
    carData["uniqueKey"] = uniqueKey
    if ul is not None:

        for li in ul.findAll('li'):
            if li is not None :
                liString = str(li).replace('amp;', '')
                if liString.find("imageShowLarge('") != -1:
                    startImg = liString.find("imageShowLarge('") + 16
                    endImg = liString.find("')")


                    imageUrl = liString[startImg:endImg]
                    # print(imageUrl)

                    try:
                        with db.cursor() as cursor:
                            sql = 'INSERT INTO IMAGE_LIST (IMG_ID, IMG_URL) VALUES (%s, %s)'
                            cursor.execute(sql, (uniqueKey,imageUrl))
                    finally:
                        None

def generate_unique_key():
    return ''.join(random.sample(CHARACTERS, 15))