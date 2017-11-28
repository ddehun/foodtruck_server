import requests


def loc2addr(lat,lng):
    #좌표를 받아서 주소를 return한다.
    key = 'C4BC0B43-232A-3C4F-86EB-4DDC8352D2D8'
    url = 'http://apis.vworld.kr/coord2jibun.do?x={}&y={}&apiKey={}&domain=www.naver.com&output=json'.format(lng,lat,key)
    
    
    res = requests.get(url)
    address = None
    if 'ADDR' in res.json():
        address = res.json()['ADDR']
    else:
        address = ' '
    return address

if __name__ == '__main__':
    print(loc2addr(36.3732403,127.3623303))
    
    
