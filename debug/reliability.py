import requests,time
'''
100번 검색하고 결과 및 시간 체크하기
'''

if __name__ == '__main__':
    ip = 'http://52.79.46.173:8081'

    keyword = ''
    location = '(36.3732445,127.3623607)'
    distance = '2000'

    iter_ = 500
    time_total = 0
    prev = None
    
    for i in range(iter_):
        start = time.time()
        res = requests.post(ip+'/search',data={'keyword':keyword,'location':location,'distance':distance})
        if prev==None:
            prev = res
            continue
        if res.json() != prev.json():
            print('WARNING!')
            break
        end = time.time()
        time_total += (end-start)
        print(time_total)
    print('search average time : {}'.format(time_total/iter_))
    
