
import statusCheckPage
import pymysql

db = pymysql.connect(host='169.56.83.89', port=3306, user='root', passwd='Cnthoth123!', db='ALLCU',
                                 use_unicode=True, charset='utf8', autocommit=True)

statusCheckPage.check(db)
db.close()