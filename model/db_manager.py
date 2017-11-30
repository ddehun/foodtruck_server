from pymongo import MongoClient,ReturnDocument
from model.util import gps2meter,distance,ctg2name
from operator import itemgetter
from model.geocoder import loc2addr
import pytz
import datetime as dt

'''
SERVER <-> DB간 method 정보
'''

class Database_manager():
    def __init__(self):
        dbstring = 'mongodb://{}:{}@{}:{}/{}'.format('ddehun','142136','13.124.230.50','27017','test')
        client = MongoClient('localhost',27017)
        db = client.test
        self.user_col = db.user
        self.foodtruck_col = db.foodtruck
        self.keyword_col = db.keyword 

    def try_login(self,data):
        '''
        로그인
        '''
        login_id_result = self.user_col.find({'id' : data['id']}).count()
        if login_id_result != 1:
            return '2',False, None
        if login_id_result >2:
            print('으아아아아아아아아아아앙ㅇ아아아아아')
        login_id = self.user_col.find({'id' : data['id'],'password':data['password']})
        login_id_result = login_id.count()
        if login_id_result != 1:
            return '3',False, None
        else:
            return '0',True, login_id[0]['type']
 
    def check_sign_in(self,data):
        '''
        회원가입 항목에 대한, DB와의 consistency 확인 ((이름-연락처) 및 ID 중복 확인))
        '''
        dupl1 = self.user_col.find({'name' : data['name'], 'phone':data['phone']}).count()
        if dupl1 != 0:#duplicated (name, phone) tuple
            print('same person signin')
            return '3',False
        dupl2 = self.user_col.find({'id':data['id']}).count()
        if dupl2 != 0:#duplicated ID
            print('\n[SIGN_IN ERROR]\nLOCATION : db_manager->check_sign_in\nduplicated id')
            return '2',False
        return '0',True
    
    def insert_sign_in(self,data):
        '''
        새로운 유저 데이터 저장
        '''
        user_id = self.user_col.insert(data)
        return user_id

    def find_foodtruck_info(self,user_id):
        '''
        user_id를 통해 푸드트럭 검색
        dic return
        '''
        data = {'name':'-1','phone':'-1','area':'-1','ctg':'-1','introduction':'-1','menulist':'-1','reviewlist':'-1','photo':'-1'}
        result = self.foodtruck_col.find_one({'id':user_id})
        if result==None: return -1,data
        for key in data:
            if key == 'phone':
                data['phone'] = split_phone(result['phone'])
            elif key in ['menulist','reviewlist']:
                data[key] = []
                if key in result:
                    for menu in result[key]:
                        data[key].append(result[key][menu])
            else:
                data[key] = result[key] 
        return 0,data
    
    def modify_foodtruck(self,data):
        update_ = {}
        for i in data:
            update_[i] = data[i]
        res = self.foodtruck_col.find_one_and_update(
                {'id':data['id']},
                {'$set':update_},
                return_document=ReturnDocument.AFTER)
        return True

    def insert_foodtruck_enroll(self,data):
        fd_id = self.foodtruck_col.insert(data)
        return fd_id
 
    def foodtruck_location(self,name):
        fd = self.foodtruck_col.find_one({'id':name})
        if 'saleslist' not in fd or fd['saleslist']=={}:
            return (0,0)
        loc = None
        cnt = -1
        for i in fd['saleslist']:
            cnt += 1
        loc = fd['saleslist'][str(cnt)]['location']
        return loc
        
    def check_foodtruck_enroll(self,data):
        modify_check = self.foodtruck_col.find({'id':data['id']}).count()
        if modify_check!=0: #푸드트럭 수정 요청
            return None
        dupl = self.foodtruck_col.find(data).count()
        if dupl >= 1:
            print('same food truck')
            return False
        dupl = self.foodtruck_col.find({'phone':data['phone']}).count()
        if dupl >=1 :
            print('휴대폰 번호 중')
            return False
        allfd = self.foodtruck_col.find()
        newname = ''
        for i in data['name'].split():
            newname+=i
            
        for fd in allfd:
            raw = fd['name']
            name = ''
            for i in raw.split():
                name += i
            if name==newname:
                print('중복된 푸드트럭 이름')
                return False     
        return True 
        
    def review_write(self,data):
        duplicating = False
        owner = self.foodtruck_col.find_one({'id' : data['ft_id']})

        #리뷰중복체크
        rls = owner['reviewlist']
        for i in rls:
            r = rls[i]
            writer = r['w_id']
            detail = r['detail']
            rating = r['rating']
            if data['w_id']==writer and data['detail']==detail and data['rating']==rating:
                duplicating = True
                print('중복 리뷰입니다')

        if not duplicating:
            if owner == None:
                print('으악!!!!!!!!!!!!!!!!!!!!!!!!!')
            cnt = 0
            if 'reviewlist' not in owner:
                pass
            else:
                for i in owner['reviewlist']:
                    cnt += 1
            update_ = {}
            for i in data:
                if i == 'ft_id':continue
                key_ = '{}.{}.{}'.format('reviewlist',cnt+1,i)
                update_[key_] = data[i]
                res = self.foodtruck_col.find_one_and_update(
                    {'id':data['ft_id']},
                    {'$set':update_},
                    upsert=True,
                    return_document=ReturnDocument.AFTER)

        return_list =  []
        fd = self.foodtruck_col.find_one({'id':data['ft_id']})
        for rev in fd['reviewlist']:
            return_list.append(fd['reviewlist'][rev])
        return return_list
    
    def menu_enroll(self,data):
        owner_check = self.foodtruck_col.find_one({'id' : data['id']}) #메뉴 등록하고자 하는 유저의 id와 일치하는 푸드트럭 소유주 존재?
        if owner_check == None:
            print('[메뉴 등록] 이런 사람이 없어요!!!!!!!!!!')
            return False
        
        if 'menulist' in owner_check:
            for i in owner_check['menulist']:
                if type(owner_check['menulist'][i]) == str: continue
                if owner_check['menulist'][i]['name'] == data['name']:
                    print('메뉴 중복')
                    return False
        update_ = {}
        for i in data:
            if i=='id':continue
            key_ = '{}.{}.{}'.format('menulist',data['name'],i)
            update_[key_] = data[i]
            res = self.foodtruck_col.find_one_and_update(
                {'id':data['id']},
                {'$set':update_},
                upsert=True,
                return_document=ReturnDocument.AFTER)
        return True
       
    def remove_menu(self,data):
        res = self.foodtruck_col.update({'id' : data['id']},
                                        {'$unset' : {'{}.{}'.format('menulist',data['name']) : ''}})
        return res

    def find_menulist_of_user(self,id_):
        menulist = []

        fd = self.foodtruck_col.find_one({'id':id_})
        for i in fd['menulist']:
            menulist.append(fd['menulist'][i])
        return menulist

    def start_sale(self,data):
        print(data['id'],end=' ')
        print('가 판매 시작, 어디서? ',end='')
        print(data['location'],end=' 에서~\n\n')
        
        check = self.foodtruck_col.find_one({'id':data['id']})
        if check == None:#푸드트럭 없는 사람이 장사 시작할
            return -1,[]

        #장사시작 및 위치 저장
        res = self.foodtruck_col.find_one_and_update(
            filter={'id':data['id']},
            update={'$set' :{'sales' : True,
                                'lat' : data['location'][0],
                                'long' : data['location'][1]}},
            upsert=True,
            return_document=ReturnDocument.AFTER)

        #Return할 메뉴 리스트
        fd = self.foodtruck_col.find_one({'id':data['id']})
        if 'menulist' not in fd: raw_menulist = []
        else: raw_menulist = fd['menulist']
        menulist = []
        for i in raw_menulist:
            menulist.append(raw_menulist[i])

        #판매여부 관련
        sales_cnt = 0
        if 'saleslist' not in fd:
            self.foodtruck_col.find_one_and_update({'id':data['id']},{'$set':{'saleslist':{}}})
            fd = self.foodtruck_col.find_one({'id':data['id']})
        #장사개시 로그를 DB에 찍어야 한다.
        current = ''
        
        ltz = pytz.timezone('Asia/Seoul')
        ldt = dt.datetime.now().replace(tzinfo=pytz.utc).astimezone(ltz)
        current = '{}-{}-{}-{}-{}-{}'.format(ldt.year,ldt.month,ldt.day,ldt.hour,ldt.minute,ldt.weekday())

        
        #2017-11-25-20-25-6(마지막껀 요일)
        for i in fd['saleslist']:
            sales_cnt += 1
        update_ = dict()
        update_['{}.{}.{}'.format('saleslist',str(sales_cnt),'begin')] = current
        update_['{}.{}.{}'.format('saleslist',str(sales_cnt),'location')] = data['location']
        update_['{}.{}.{}'.format('saleslist',str(sales_cnt),'kor_location')] = loc2addr(data['location'][0],data['location'][1])
        self.foodtruck_col.find_one_and_update({'id':data['id']},{'$set':update_})            
        return res, menulist
    
    def end_sale(self,data):
        print(data['id'],end=' ')
        print('가 판매 종료, 어디서? ',end='')
        print(data['location'],end=' 에서~\n\n')

        res = self.foodtruck_col.find_one_and_update(
            filter={'id':data['id']},
            update={'$set' :{'sales' : False,
                                'lat' : data['location'][0],
                                'long' : data['location'][1]}},
            upsert=True,
            return_document=ReturnDocument.AFTER)

        sales_cnt = 0
        fd = self.foodtruck_col.find_one({'id':data['id']})
        for i in fd['saleslist']:
            sales_cnt += 1
        sales_cnt -= 1
        
        current = ''

        ltz = pytz.timezone('Asia/Seoul')
        ldt = dt.datetime.now().replace(tzinfo=pytz.utc).astimezone(ltz)
        current = '{}-{}-{}-{}-{}-{}'.format(ldt.year,ldt.month,ldt.day,ldt.hour,ldt.minute,ldt.weekday())
        #2017-11-25-20-25-6(마지막껀 요일)

        update_ = dict()
        update_['{}.{}.{}'.format('saleslist',str(sales_cnt),'end')] = current
        update_['{}.{}.{}'.format('saleslist',str(sales_cnt),'total_price')] = data['total_price']
        self.foodtruck_col.find_one_and_update({'id':data['id']},{'$set':update_})
        return res
   
    def fd_sale_list(self,user_id):
        fd = self.foodtruck_col.find_one({'id':user_id})
        if fd==None or'saleslist' not in fd:
            return []
        saleslist = fd['saleslist']
        '''
	date : ‘2017년 11월 25일 토요일’
	begin : ‘08:25’
	end   :  ‘15:24’
	total_price : ‘123123’
	location : ‘유성구 구성동’
        '''
        res = []
        #2017-11-25-20-25-6(마지막껀 요일)
        days = '월화수목금토일'
        for s in saleslist:
            salelist_idx = s
            s = saleslist[s]
            if 'begin' not in s or 'end' not in s: continue
            begin_ = s['begin'].split('-')
            end_ = s['end'].split('-')
            date = begin_[0]+'년 '+begin_[1]+'월 '+begin_[2]+'일 ' + days[int(begin_[-1])]+'요일'
            if len(begin_[4])==1:begin_[4] = '0'+begin_[4]
            begin = begin_[3]+':'+begin_[4]
            if len(end_[4])==1:end_[4] = '0'+end_[4]
            end = end_[3]+':'+end_[4]
            total_price = s['total_price']

            if 'kor_location' in s:
                location = s['kor_location']
            else:
                address = loc2addr(s['location'][0],s['location'][1])
                location = address#str(s['location'])
                kor_loc_add = self.foodtruck_col.find_one_and_update(
                    {'id':user_id},
                    {'$set':{'saleslist.{}.kor_location'.format(salelist_idx) : location}},
                    upser=True,
                    return_document = ReturnDocument.AFTER)
                
            dic  = {'date':date, 'begin':begin, 'end':end, 'total_price':total_price, 'location':location}
            res.append(dic)

        #날짜,시간 순으로 매출정보 정리하기
        res= sorted(res,key=itemgetter('date'),reverse=True)
        final_result = []
        tmp = res[0]['date']
        ondate = []
        for i in res:
            i['sortkey'] = '0'*(5-len(i['end']))+ i['end'][:-3]+i['end'][-2:]
            if i['date']==tmp:
                ondate.append(i)
            else:
                ondate = sorted(ondate,key=itemgetter('end'))
                final_result += ondate
                ondate=[i]
                tmp=i['date']
        ondate = sorted(ondate,key=itemgetter('sortkey'))
        final_result += ondate

        print('매출정보 반환')
        for i in final_result:
            del i['sortkey']
        return final_result
        
    def recommend_keyword(self,location):
        '''
        유저들의 장소에 따른 검색 키워드를 기반으로, 키워드 추천
        '''
        res = self.keyword_col.find()
        counter = []
        for keyword in res:#각 키워드별로, 주변에서 검색된 횟수를 counting한다.
            cnt = 0
            for idx in keyword['his']:
                loc = keyword['his'][idx]['location']
                dis = gps2meter(location,loc)*1000
                if dis<2000:
                    cnt += 1
            counter.append({'name':keyword['name'], 'count':cnt})
        
        counter = sorted(counter, key=itemgetter('count'), reverse=True)

        result_ = []
        for i in counter[:3]:
            result_.append(i['name'])
      
        if len(result_)<3:
            condition = {'distance':2000,'location':location,'keyword':''}
            search_ = search_algorithm(self.foodtruck_col,condition)
            for j in range(len(result_)):
                result_.append(search_[j]['name'])
                if len(result_)==3: break
            if len(result_)<3:
                print('데이터 부족. 주변에 아무것도 X')
                for i in range(3-len(result_)):
                    result_.append(' ')

        print('#키워드 추천 최종 리스트#')
        print(result_)
        return result_

    def search_foodtruck(self,condition):
        #푸드트럭 검색
        results = search_algorithm(self.foodtruck_col, condition)

        #검색 키워드 저장
        keyword = condition['keyword'] if condition['keyword'] != '' else None
        if keyword!=None:
            curr_cnt = 1
            res = self.keyword_col.find_one({'name':keyword})
            if res == None:
                self.keyword_col.insert({'name':keyword})
                update_ = {'$set':{'his.{}.location'.format(curr_cnt):condition['location']}}
                res = self.keyword_col.find_one_and_update({'name':keyword},update_)
            else:
                for i in res['his']:
                    curr_cnt += 1
                update_ = {'$set' : {'his.{}.location'.format(curr_cnt):condition['location']}}
                res = self.keyword_col.find_one_and_update({'name':keyword},update_)
 
        return [len(results),results]

    def find_photo(self,f_id):
        fd = self.foodtruck_col.find_one({'id':f_id})
        photo = fd['photo']
        return photo
    
    def favorite_check(self,user_id,f_id):
        curr = self.user_col.find_one({'id':user_id})
        if 'favorites' not in curr:
            self.user_col.find_one_and_update({'id':user_id},{'$set':{'favorites':[]}})
            return 0
        if f_id not in curr['favorites']:
            return 0
        else:
            return 1

    def favorite_change(self,user_id,f_id,curr):
        fd = self.user_col.find_one({'id':user_id})
        curr = True if (int(curr)==0) else False

        ls = fd['favorites'] if 'favorites' in fd else []

        if curr:#즐겨찾기 등록 취소
            print('즐겨찾기 취소 시도')
            ls.remove(f_id) 
        else:
            print('즐겨찾기 등록 시도')
            if f_id in ls: print('으악!!!!!!!!!!!~~~~~~~')
            ls.append(f_id)
        to_db = self.user_col.find_one_and_update({'id':user_id},{'$set':{'favorites':ls}})
        after =  self.user_col.find_one({'id':user_id})['favorites']
        res = 1
        if curr and 'f_id' not in after: res = 0
        if not curr and 'f_id' in after: res = 0
        return res

    def favorite_list(self,user_id):
        fd = self.user_col.find_one({'id':user_id})
        if 'favorites' not in fd: return []
        favorites = fd['favorites']
	if favorites==[]: return []
        return_ = []
        for f_id in favorites:
            dic = {'area':None,'id':f_id,'introduction':None,'name':None,'phone':None,'ctg':None,'menulist':None,'reviewlist':None}
            data = self.foodtruck_col.find_one({'id':f_id})
            keys = list(dic.keys())
            dic = listpack(data,keys)
        return_.append(dic)
        return return_


def search_algorithm(fd_col,condition):
    #Keyword, location을 통해 현재 영업중인 푸드트럭을 찾는다. 
    results = []
    location_results = []
    
    #0. 위치기반 검색
    threshold = int(condition['distance'])#거리제한

    print('{}m이내 푸드트럭 검색'.format(threshold))
    pivot_location = condition['location']    

    total = fd_col.find()#fd_col.find({'sales':True})

    for fd in total:
        if 'name' not in fd:continue
        if 'lat' not in fd: continue
        raw_loc = (float(fd['lat']),float(fd['long']))
        print('두 푸드트럭간의 거리 : ',end='')
        dis = gps2meter(pivot_location,raw_loc)
        dis = dis*1000 #km to meter
        print(dis,end='m\n')
        if dis < threshold:
            del fd['_id']
            if fd not in location_results:
                fd['phone'] = split_phone(fd['phone'])
                fd['distance'] = dis
                location_results.append(fd)
    
    #1. 푸드트럭 이름 검색
    if 'keyword' in condition:
        byname_res = []
        for fd in location_results: #김밥이나 김밥천국을 검색해도 김밥천국이 나옴
            if condition['keyword'] in fd['name']:
                if fd not in results:
                    results.append(fd)

    #2. 카테고리 검색 (키워드 안에 카테고리 단어가 있을 경우)
    name2int, int2name = ctg2name(1,True)
    byctg_res = []
    if 'keyword' in condition and condition['keyword'] in name2int.keys():#카테고리
        ctg = name2int[condition['keyword']]
        for fd in location_results:
            if fd['ctg'] == str(ctg):
                if  '_id' in fd:
                    del fd['_id']
                if fd not in results:
                    results.append(fd)

    #최종결과 거리로 sorting
    final_results = []
    for i in range(len(results)):
        final_results.append(listpack(results[i]))
    final_results = sorted(final_results,key=itemgetter('distance'))#가까운 푸드트럭부터 반
    for i in range(len(final_results)):
        final_results[i]['distance'] = str(int(float(final_results[i]['distance'])))

    print('\n#최종검색결과#')
    for i in final_results:
        print(i['name'])
    return final_results


def split_phone(phone):
    phone = str(phone)
    return phone[:3]+'-'+phone[3:-4]+'-'+phone[-4:]


def listpack(data,condition=None):
    rekeys = ['menulist','reviewlist']
    newdata = {}

    for key in data:
        if condition!=None and key not in condition:
            continue
        if key=='_id':continue
        if key in rekeys:
            tmp = []
            for cnt in data[key]:#메뉴이름이나 번호 등
                tmp.append(data[key][cnt])
            if key=='menulist':
                tmp = sorted_ = sorted(tmp,key=itemgetter('name'))
            newdata[key]=tmp
        else:
            newdata[key]=data[key]

    for i in rekeys:
        if i not in newdata:
            newdata[i] = []    
    return newdata


