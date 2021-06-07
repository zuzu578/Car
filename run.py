import avgPrice
import bobae
import encar
import ku
import statusCheckPage
import checkExist
import pymysql
import kcar

db = pymysql.connect(host='169.56.83.89', port=3306, user='root', passwd='Cnthoth123!', db='ALLCU',
                                 use_unicode=True, charset='utf8', autocommit=True)
# ku.kuCrawling(db)
# encar.encarCrawling(db)
bobae.bobaeCrawling(db)
# kcar.kcarCrawling(db)
# statusCheckPage.statusCheckPage(db)
# statusCheckPage.check(db)
# checkExist.checkExist(db)
# avgPrice.avgPrice(db)
db.close()