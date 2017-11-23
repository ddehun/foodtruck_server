from pymongo import MongoClient,ReturnDocument
from model.util import gps2meter,distance,ctg2name
from operator import itemgetter
'''
SERVER <-> DB간 method 정

'''

class DB_operation():
    def __init__(self):
        client = MongoClient('localhost',27017)
        db = client.test
        self.user_col = db.user
        self.foodtruck_col = db.user
        

class Database_manager():
    def __init__(self):
        dbstring = 'mongodb://{}:{}@{}:{}/{}'.format('ddehun','142136','13.124.230.50','27017','test')
        client = MongoClient('localhost',27017)
        db = client.test
        self.user_col = db.user
        self.foodtruck_col = db.foodtruck
    def remove_menu(self,data):
        res = self.foodtruck_col.update({'id' : data['id']},
                                        {'$unset' : {'{}.{}'.format('menulist',data['name']) : ''}})
        return res
        
    def review_write(self,data):
        owner = self.foodtruck_col.find_one({'id' : data['ft_id']})
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
        
    def find_menulist_of_user(self,id_):
        menulist = []

        fd = self.foodtruck_col.find_one({'id':id_})
        for i in fd['menulist']:
            menulist.append(fd['menulist'][i])
        return menulist

    
        
    def check_foodtruck_enroll(self,data):
        modify_check = self.foodtruck_col.find({'id':data['id']}).count()
        if modify_check!=0: #푸드트럭 수정 요청
            return None
        dupl = self.foodtruck_col.find(data).count()
        if dupl >= 1:
            print('same food truck')
            return False
        dupl = self.foodtruck_col.find({'phone':data['phone']}).count()
        #dupl = self.foodtruck_col.find({'id':data['id']}).count()
        if dupl >=1 :
            print('휴대폰 번호 중')
            return False
        return True 

    def start_sale(self,data):
        print(data['location'])
        print(data['location'][0])
        res = self.foodtruck_col.find_one_and_update(
            filter={'id':data['id']},
            update={'$set' :{'sales' : True,
                                'lat' : data['location'][0],
                                'long' : data['location'][1]}},
            upsert=True,
            return_document=ReturnDocument.AFTER)
        return res

    def insert_foodtruck_enroll(self,data):
        fd_id = self.foodtruck_col.insert(data)
        return fd_id
    
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

    def find_foodtruck_info(self,user_id):
        '''
        user_id를 통해 푸드트럭 검색
        dic return
        '''
        data = {'name':'-1','phone':'-1','area':'-1','ctg':'-1','introduction':'-1','menulist':'-1'}
        result = self.foodtruck_col.find_one({'id':user_id})
        if result==None: return -1,data
        for key in data:
            if key == 'menulist':
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
        
    def search_foodtruck(self,condition):
        #푸드트럭 검색
        results = search_algorithm(self.foodtruck_col, condition)

        print('\n\n\n\n\n')
        print(search_algorithms(self.foodtruck_col,condition))
        print('\n\n\n\n\n')


              
        #여기서 search한걸 sorting하는 알고리즘 추가? 다른데서 짜서 import하기
        return [len(results),results]


def search_algorithms(fd_col,condition):
    #Keyword, location을 통해 현재 영업중인 푸드트럭을 찾는다.
    '''
    여기에, 판매중인 애들만 고르는 조건 ex: on_sale : true 이런거도 넣어야함

    1. 2km안에 꺼 중에서
    2. 키워드 검색하기

    인데, 지금은 없으니깐 그냥 함!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''
    
    results = []
    #1. 푸드트럭 이름 검색
    if 'keyword' in condition:# and condition['keyword'] != '':
        byname_res = fd_col.find({'name':condition['keyword']})#김밥나라 -> 김밥나라
        if byname_res.count() != 0:
            for i in byname_res:
                del i['_id']
                results.append(i)
        
        byname_res = fd_col.find()
        for fd in byname_res:
            if condition['keyword'] in fd['name']:#김밥 쳐도 김밥나라
                del fd['_id']
                if fd not in results:
                    results.append(fd)
        
    #2. 카테고리 검색 (키워드 안에 카테고리 단어가 있을 경우)
    
    name2int, int2name = ctg2name(1,True)
    if 'keyword' in condition and condition['keyword'] in name2int.keys():# and condition['keyword'] != '':
        ctg = name2int[condition['keyword']]
        byctg_res = fd_col.find({'ctg':str(ctg)})
        for i in byctg_res:
            del i['_id']
            if i not in results:
                results.append(i)


    #3. 위치기반 검색

    threshold = 2 #2km이내만 검색
    pivot_location = condition['location']    
    total = fd_col.find() #이걸 지역별로 나누는게 좋겠다. 충청 지역만 검색! 이런식으로 아닌가?아닌듯/근데뭔가 좁힐수있는 조건이 나중엔 필요할듯
    for fd in total:
        if 'lat' not in fd: continue
        raw_loc = (float(fd['lat']),float(fd['long']))
        print('두 푸드트럭간의 거리 : ',end='')
        dis = gps2meter(pivot_location,raw_loc)
        print(dis,end='km\n')
        if dis < 2:
            del fd['_id']
            if fd not in results:
                results.append(fd)

    #4. 키워드 검색
    final_results = []
    for i in range(len(results)):
        final_results.append(listpack(results[i]))
        
    return final_results


def listpack(data):
    rekeys = ['menulist','reviewlist']
    newdata = {}

    for key in data:
        if key=='_id':continue
        if key in rekeys:
            tmp = []
            for cnt in data[key]:#메뉴이름이나 번호 등
                tmp.append(data[key][cnt])
            newdata[key]=tmp
        else:
            newdata[key]=data[key]

    for i in rekeys:
        if i not in newdata:
            newdata[i] = []
    
    return newdata



def search_algorithm(fd_col,condition):
    #Keyword, location을 통해 현재 영업중인 푸드트럭을 찾는다.
    '''
    여기에, 판매중인 애들만 고르는 조건 ex: on_sale : true 이런거도 넣어야함

    1. 2km안에 꺼 중에서
    2. 키워드 검색하기

    인데, 지금은 없으니깐 그냥 함!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''
    
    results = []

    location_results = []
    
    #0. 위치기반 검색
    threshold = 10000000000000000000000000000000000 #2km이내만 검색
    pivot_location = condition['location']    
    total = fd_col.find()


    '''
    for fd in total:
        if 'lat' not in fd: continue
        raw_loc = (float(fd['lat']),float(fd['long']))
        print('두 푸드트럭간의 거리 : ',end='')
        dis = gps2meter(pivot_location,raw_loc)
        print(dis,end='km\n')
        if dis < threshold:
            del fd['_id']
            if fd not in results:
                fd['distance'] = dis
                location_results.append(fd)
    '''
    location_results = list(fd_col.find())#푸드트럭 개시가 완료되면 바로위에 주석 지우고 ㄱㄱ
    
    print('##거리 안의 푸드트럭들##\n{}'.format(location_results))
    
    #1. 푸드트럭 이름 검색
    if 'keyword' in condition:
        byname_res = []
        for fd in location_results: #김밥이나 김밥천국을 검색해도 김밥천국이 나옴
            if condition['keyword'] in fd['name']:
                del fd['_id']
                if fd not in results:
                    results.append(fd)


    #2. 카테고리 검색 (키워드 안에 카테고리 단어가 있을 경우)
    name2int, int2name = ctg2name(1,True)
    byctg_res = []
    if 'keyword' in condition and condition['keyword'] in name2int.keys():#카테고리
        ctg = name2int[condition['keyword']]
        for fd in location_results:
            if fd['ctg'] == str(ctg):
                del fd['_id']
                results.append(fd)

    '''         
    if results == []:
        for i in location_results:
            results.append(i)
    '''

            
    final_results = []
    for i in range(len(results)):
        final_results.append(listpack(results[i]))


    sorted_ = sorted(final_results,key=itemgetter('distance'))#가까운 푸드트럭부터 반

        
    return final_results

