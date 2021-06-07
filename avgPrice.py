import statistics
import numpy as np
import scipy.stats


def mean_confidence_interval(data, confidence=0.20):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

def avgPrice(db) :
    model = '쏘나타'
    year = '2015'

    cursor = db.cursor()
    selectSql = """select PRICE FROM CAR_DATA WHERE TITLE LIKE '%"""+model+"""%' AND CAR_YEAR = """+year+""" AND PRICE != 0;"""
    cursor.execute(selectSql)
    data = cursor.fetchall()

    items1 = []

    for x in data:
        items1.append(x[0])

    a = np.array(items1)

    median = statistics.median(items1)

    print('최소값 >>>' + str(min(items1)))
    print('최대값 >>>' + str(max(items1)))
    print('평균값 >>>' + str(np.mean(a)))
    print('중간값 >>>' + str(median))

    avg, h = mean_confidence_interval(items1)
    minMedian = avg - h
    maxMedian = avg + h

    print('신뢰 편차값 >>>' + str(h))
    print('신뢰 최소값 >>>' + str(minMedian))
    print('신뢰 최대값 >>>' + str(maxMedian))

    cursor = db.cursor()
    selectSql = """select PRICE FROM CAR_DATA WHERE TITLE LIKE '%"""+model+"""%' AND CAR_YEAR = """+year+""" AND PRICE >= """+str(minMedian)+""" AND PRICE <= """+str(maxMedian)
    cursor.execute(selectSql)
    data2 = cursor.fetchall()

    items2 = []
    for x in data2:
        items2.append(x[0])

    a2 = np.array(items2)
    print('신뢰구간 내 평균값 >>>' + str(np.mean(a2)))