'''
schema.py
프로젝트 내의 데이터 타입들을 보다 효율적으로 관리

TYPE check(phone은 무적권 int 이렇게)도 해야할텐데~

'''

class Review_schema():
    def __init__(self,data):
        self.keys = ['ft_id','w_id','rating','detail']
        self.data = data

        self.empty_error = False

        for i in self.keys:
            if self.data[i] == '':
                self.empty_error = True

    def dictionalize(self):
        a = {}
        for i in self.keys:
            a[i] = self.data[i]
        return a

class Menu_schema():
    def __init__(self,data):
        self.keys = ['id','name','price','ingredients']
        self.data = data

        self.empty_error = False
        for key in self.data:
            if data[key] == '':
                self.empty_error = True
        
    def dictionalize(self):
        dic = dict()
        ingre = []
        for i in self.data:
            dic[i] = self.data[i]
        return dic
    
            
class Search_schema():
    def __init__(self,data):
        self.keys = ['keyword','location']#['price','distance','hate','menu','keyword']
        self.data = data

        self.empty_error = False
        if self.empty_error:
            print('\n[SEARCH ERROR]\nLOCATION : Search_schema->init\n빈조건 검색 error\n')

        self.error,self.error_key,self.passed_key = self.check_val(data)
        self.keyword = data['keyword'] if 'keyword' in data else None
        self.location = data['location'] if 'location' in data else None
    def dictionalize(self):

        dic = dict()
        for i in self.keys:
            if i in self.data.keys():
                if i =='location':
                    raw_loc = self.data['location']
                    raw_loc = (float(raw_loc.split(',')[0][1:]),float(raw_loc.split(',')[1][:-1]))
                    dic[i] = raw_loc
                else:
                    dic[i] = self.data[i]
        return dic
            
    def check_val(self,data):
        return 1,1,1
        passed_key = []
        error,error_key = False,None        
        for key in data:
            if key not in self.keys:
                print('\n[SEARCH ERROR]\nLOCATION : Search_schema->check_val\nkey error\n')
                error , error_key = True, key
                break
        for key in self.keys:
            if key not in data.keys:#검색 조건에서 생략된 key
                passed_key.insert(key)
        return error,error_key,passed_key

        
class Login_schema():
    def __init__(self,data):
        self.keys = ['id','password']
        self.empty_error = False
        for i in data:
            if data[i] == '':
                self.empty_error = True
        self.error,self.error_key,self.missing,self.missing_key = self.check_val(data)

        if self.error or self.missing_key:
            print('\n[LOGIN ERROR]\nLOCATION : Login_schema->__init__\nkey error\n')
        if self.error: #이상한 key가 들어옴
            print('{} is not key value'.format(self.error_key))
        if self.missing:#필요한 key가 안들어옴
            print('@{}@ expected, but not come'.format(self.missing_key))
        
        self.id = data['id']
        self.password = data['password']
        
        
    def dictionalize(self):
        dic = dict()
        dic['id'] = self.id
        dic['password'] = self.password
        return dic
        
    def check_val(self,data):
        error = False
        error_key = None
        for i in data:
            if i not in self.keys:
                error = False
                error_key = i
                break
        missing = False
        missing_key = None
        for i in self.keys:
            if i not in data:
                missing = True
                missing_key = i
                break
        return error,error_key,missing,missing_key  


class Foodtruck_enroll_schema():
    def __init__(self,data):
        self.phone_error = False
        self.area_error = False
        self.category_error = False
        try:
            int(data['phone'])
        except:
            self.phone_error = True
        if data['area'] not in [str(i) for i in range(1,10)]:
            self.area_error = True
        if 'ctg' not in data or int(data['ctg']) not in range(1,14):
            print('카테고리 에러')
            print(data['ctg'])      
            self.category_error = True
        self.keys = ['id','name','phone','area','ctg','introduction']
        self.data = data
        if not bool(self.data):
            print('\n[ERROR]푸드트럭 등록 에러\nFoodtruck_enroll_schema\n데이터가 비었음')
        self.error,self.error_key = self.check_val(data)        

        for i in data:
            if data[i] == '':
                self.error = True
        
        if not self.error:
            self.ctg = data['ctg']
            self.id = data['id']
            self.name = data['name']
            self.phone = data['phone']
            self.area = data['area']
            self.introduction = data['introduction']
        
    def dictionalize(self):
        data = self.data
        a = dict()
        a['id'] = data['id']
        
        origin_name = data['name']
        final_name = ''
        splited = origin_name.split(' ')
        for i in splited:
            final_name += i
        a['name'] = final_name#data['name'] #모든 푸드트럭의 이름에서 띄어쓰기를 없앤다.
        
        a['phone'] = data['phone']
        a['ctg'] = data['ctg']
        a['area'] = data['area']
        a['introduction'] = data['introduction']
        return a
    
    def check_val(self,data):
        error,error_key = False, None
        for key in data:
            if key not in self.keys:
                error = False
                error_key = key
                break
        a = []
        for i in data.keys():
            a.append(i)
        a.sort()
        self.keys.sort()
        if a != self.keys:
            print('key error! \n{} is given.\n{} is answer'.format(data.keys, self.keys))
            error = True
        return error,error_key
    

class Foodtruck_modify_schema():
    def __init__(self,data):
        pass
    
    def dictionalize(self):
        pass
    
    def check_val(self,data):
        pass

    
class User_schema():
    def __init__(self, data):
        print('user schema visited')
        self.empty_error = False
        for i in data:
            if data[i] == '':
                self.empty_error = True
        
        self.keys = ['name','phone','type','id','password']
        self.type_error = False #To be implemented....
        self.error,self.error_key,self.missing,self.missing_key,type_error,type_error_key = self.check_val(data)
        if data['type'] not in ['Seller','Purchaser']:
            self.error = True
            print('[회원가입 에러] Purchaser나 Seller가 아니에요')
        
        if not (self.error or self.missing or self.type_error):
            self.id = data['id']
            self.password = data['password']
            self.phone = data['phone']
            self.type = data['type']
            self.name = data['name']
            print('fine user schema')
        else:
            print('[Warning] Data error')
            if self.error: #이상한 key가 들어옴
                print('{} is not key value'.format(self.error_key))
            if self.missing:#필요한 key가 안들어옴
                print('@{}@ expected, but not come'.format(self.missing_key))
            if self.type_error:#phone type != int
                print('phone number is not int/ {} is given'.format(self.phone))
            self.id = None
            self.password = None
            self.phone = None
            self.type = None
            self.name = None
            print('error user schema')
            
    def dictionalize(self):
        dic = {}
        dic['id'] = self.id
        dic['password'] = self.password
        dic['name'] = self.name
        dic['type'] = self.type
        dic['phone'] = self.phone
        return dic
        
    def check_val(self,data):
        error = False
        error_key = None
        for i in data:
            if i not in self.keys:
                error = False
                error_key = i
                break
        missing = False
        missing_key = None
        for i in self.keys:
            if i not in data:
                missing = True
                missing_key = i
                break

        type_error = False
        type_error_key = None
        try:
            int(data['phone'])
        except ValueError:
            type_error = True
            type_error_key = 'phone'
        
        return error,error_key,missing,missing_key,type_error,type_error_key


    

if __name__ == '__main__':
    data  = {'name' : 'asd','phone' : 123,'type':1,'id':'ddehun'}#,'password':1234}
    us = User(data)
    print(us.id)
    
