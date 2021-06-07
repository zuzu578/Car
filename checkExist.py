import requests
import urllib3
from bs4 import BeautifulSoup

def checkExist(db):
    cursor = db.cursor()
    selectSql = """select CAR_IDX,LINK_URL,SITE,IMAGE_ID from CAR_DATA"""
    cursor.execute(selectSql)
    data = cursor.fetchall()

    for x in data:
        try:
            carIdx = str(x[0])
            url = str(x[1])
            site = str(x[2])
            imageId = str(x[3])
            print(url)

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            req = requests.get(url, verify=False)

            soup = BeautifulSoup(req.content.decode('euc-kr', 'replace'), 'lxml')

            if site == '보배드림':
                groupInfo = soup.find('div', attrs={'class': 'group-info'})
                if groupInfo is None:
                    deleteCarData(carIdx,imageId,db)
            elif site == 'SK엔카':
                productFloating = soup.find('div', attrs={'class': 'product_floating'})
                if productFloating is None:
                    deleteCarData(carIdx,imageId,db)
            elif site == '전국자동차매매사업조합연합회':
                carDetailDiv = soup.find('div', attrs={'class': 'car-detail'})
                if carDetailDiv is None:
                    deleteCarData(carIdx,imageId,db)

        except Exception as ex:
            print("Exception >>> " + str(ex))


def deleteCarData(idx,imageId,db):
    with db.cursor() as cursor:
        sql = 'DELETE FROM CAR_DATA WHERE CAR_IDX = '+idx
        cursor.execute(sql)

        imageDeleteSql = 'DELETE FROM IMAGE_LIST WHERE IMG_ID = ' + imageId
        cursor.execute(imageDeleteSql)
    db.commit()
    print("DELETE IDX >>> "+ idx)