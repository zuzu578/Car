import json

import urllib3
from bs4 import BeautifulSoup

import requests

def statusCheckPage(db):

    cursor = db.cursor()
    selectSql = """select CAR_IDX,CAR_NUM from CAR_DATA where STATUS_CHECK IS NULL"""
    cursor.execute(selectSql)
    data = cursor.fetchall()

    for x in data:
        try:
            carIdx = str(x[0])
            carNum = str(x[1])
            status = ""

            print(carIdx)

            if carNum is None or carNum == '번호판없음':
                print("none")
                status = "none"
            else:
                # url = 'http://office.kaat.kr/office/rest/extservice/OUT4511?CAR_REG_NO='+carNum
                url = 'https://www.car365.go.kr/web/program/soldvehicleData.do?guild=koreacarmarket&clientIp=&vhrno='+carNum
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                req = requests.get(url, verify=False)

                soup = BeautifulSoup(req.content.decode('utf-8', 'replace'), 'lxml')

                soup = str(soup)

                if soup.find('해당 차량번호는 존재하지 안습니다.') != -1:
                    print("none")
                    status = "none"
                else:
                    print("success")
                    status = url

            sql = """UPDATE CAR_DATA SET STATUS_CHECK =%s WHERE CAR_IDX=%s """
            cursor.execute(sql, (status,carIdx))
            db.commit()

        except Exception as ex:
            print("Exception >>> " + str(ex))


def check(db):
    cursor = db.cursor()
    selectSql = """select CAR_IDX,CAR_NUM from CAR_DATA where REAL_CHECK IS NULL"""
    cursor.execute(selectSql)
    data = cursor.fetchall()

    for x in data:

        try:
            carIdx = str(x[0])
            carNum = str(x[1])

            print(carIdx)

            mainUrl = 'https://www.car365.go.kr/web/program/soldvehicleData.do'
            # carNum = '43가0140'

            koreacarmarketUrl = mainUrl + '?guild=koreacarmarket&clientIp=&vhrno='+carNum
            # url = 'https://www.car365.go.kr/web/program/soldvehicleData.do?guild=car365&clientIp=&vhrno=43가0140'

            print(koreacarmarketUrl)

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            headers = {'Referer': mainUrl}
            req = requests.get(koreacarmarketUrl, headers=headers,verify=False)

            dict = json.loads(req.content.decode('utf-8', 'replace'))

            print('koreacarmarket ----------------')
            print(dict)

            if dict['GUILD_TS_SALE'] == "Y":
                print('success')

                sql = 'INSERT INTO CAR_REAL_CHECK (CAR_IDX, REAL_CHECK_GUBUN, REAL_CHECK_RESULT_CODE, REAL_CHECK_ERRORMSG, REAL_CHECK_TYPE, REAL_CHECK_MODEL,REAL_CHECK_USE,' \
                      'REAL_CHECK_CNM,REAL_CHECK_DATE,REAL_CHECK_SALE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql, (carIdx, dict['GUILD_GUBUN'], dict['GUILD_RESULT_CODE'], dict['GUILD_ERRORMSG'],
                                     dict['GUILD_TYPE'], dict['GUILD_CAR_MODEL'], dict['GUILD_CAR_USE'],
                                     dict['GUILD_CAR_FIRSTDATE'], dict['GUILD_TS_CNM'], dict['GUILD_TS_SALE']))
                db.commit()

            else:
                setCookie = req.headers.get('Set-Cookie').split(';')
                soldVehicleCode = str(setCookie[0])

                if soldVehicleCode.find('soldVehicleCode=') != -1:

                    soldVehicleCodeValue = soldVehicleCode.replace('soldVehicleCode=','').replace('\"','')
                    # print('soldVehicleCodeValue>>>'+soldVehicleCodeValue)

                    if soldVehicleCodeValue != "":
                        carkuUrl = mainUrl + '?guild=carku&clientIp=&vhrno='+carNum
                        cookies = {'soldVehicleCode': soldVehicleCodeValue}
                        req2 = requests.get(carkuUrl, headers=headers,cookies=cookies, verify=False)

                        dict2 = json.loads(req2.content.decode('utf-8', 'replace'))
                        print('carku ----------------')
                        print(dict2)

                        sql = 'INSERT INTO CAR_REAL_CHECK (CAR_IDX, REAL_CHECK_GUBUN, REAL_CHECK_RESULT_CODE, REAL_CHECK_ERRORMSG, REAL_CHECK_TYPE, REAL_CHECK_MODEL,REAL_CHECK_USE,' \
                              'REAL_CHECK_CNM,REAL_CHECK_DATE,REAL_CHECK_SALE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                        cursor.execute(sql,
                                       (carIdx, dict2['GUILD_GUBUN'], dict2['GUILD_RESULT_CODE'], dict2['GUILD_ERRORMSG'],
                                        dict2['GUILD_TYPE'], dict2['GUILD_CAR_MODEL'], dict2['GUILD_CAR_USE'],
                                        dict2['GUILD_CAR_FIRSTDATE'], dict2['GUILD_TS_CNM'], dict2['GUILD_TS_SALE']))

                        car365Url = mainUrl + '?guild=car365&clientIp=&vhrno='+carNum
                        req3 = requests.get(car365Url, headers=headers,cookies=cookies, verify=False)

                        dict3 = json.loads(req3.content.decode('utf-8', 'replace'))
                        print('car365 ----------------')
                        print(dict3)

                        sql = 'INSERT INTO CAR_REAL_CHECK (CAR_IDX, REAL_CHECK_GUBUN, REAL_CHECK_RESULT_CODE, REAL_CHECK_ERRORMSG, REAL_CHECK_TYPE, REAL_CHECK_MODEL,REAL_CHECK_USE,' \
                              'REAL_CHECK_CNM,REAL_CHECK_DATE,REAL_CHECK_SALE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                        cursor.execute(sql,
                                       (carIdx, '국토교통부', dict3['GUILD_RESULT_CODE'], dict3['GUILD_ERRORMSG'],
                                        dict3['GUILD_TYPE'], dict3['GUILD_CAR_MODEL'], dict3['GUILD_CAR_USE'],
                                        dict3['GUILD_CAR_FIRSTDATE'], dict3['GUILD_TS_CNM'], dict3['GUILD_TS_SALE']))
                        db.commit()

                else:
                    print('fail')

            sql = """UPDATE CAR_DATA SET REAL_CHECK ='Y' WHERE CAR_IDX=%s """
            cursor.execute(sql, carIdx)
            db.commit()

        except Exception as ex:
            print("Exception >>> " + str(ex))