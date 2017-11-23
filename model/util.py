'''
기타 함수들
'''
from geopy.distance import great_circle

def ctg2name(ctg ,dic=False):
    '''
    카테고리 넘버를 받으면 카테고리에 해당하는 걸 준다. 으악!
    '''
    name2int = {
        '꼬치' : 1,
        '튀김' : 2,
        '피자' : 3, '치킨' : 4,'분식':5,'면':6,'철판':7,'패스트푸드':8,'라이스':9,
        '디저트':10,'음료':11,'기타':12}
    int2name=dict()

    for key in name2int:
        int2name[name2int[key]]=key
    
    if dic:
        return name2int,int2name
    return int2name[ctg]

def gps2meter(loc1,loc2):
    loc1 = tuple(loc1)
    loc2 = tuple(loc2)
    miles = great_circle(loc1,loc2).miles
    factor = 0.62137119
    km = miles/factor
    return km

def distance(loc1,loc2):
    twice = pow(loc1[0]-loc2[0],2)+pow(loc1[1]-loc2[1],2)
    once = pow(twice,0.5)
    return once

if __name__ == '__main__':
    a,b = ctg2name(12,True)
