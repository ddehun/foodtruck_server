from flask import Flask, request, make_response, json, Response
from model.db_manager import Database_manager
from model.schema import User_schema,Login_schema,Foodtruck_enroll_schema,Search_schema, Menu_schema, Review_schema
import sys
from geopy.distance import great_circle
#sys.path.append('.') #1120/이거 왜 했더
'''
CS408 Flask Server
'''

application = Flask(__name__)
#application.secret_key = 'secret_key'
dbman = Database_manager()

def jsonify(s,data=None):
    response_data = dict()
    response_data['status'] = s
    if data:
        for key in data:
            response_data[key] = data[key]
    res = json.dumps(response_data,ensure_ascii=False)
    return Response(res,content_type="application/json; charset=utf-8")

@application.route('/',methods=['GET'])
def main():
    print('Welcome to CS408 TEAM16 Server!')
    return('Welcome to CS408 TEAM16 Server!')


@application.route('/sign_in',methods=['POST'])
def sign_in():
    print('[회원가입 요청]')
    input_data = request.form
    print(input_data)

    #input data check
    if not bool(request.form):
        print('len == 0)')
        return jsonify('1')
    user_schema = User_schema(input_data)
    if user_schema.error or user_schema.missing or user_schema.type_error:#input data error, See server log msg
        print('[ERROR]sign_in error')
        return jsonify('1')
    if user_schema.empty_error:
        print('비어있는 정보가 있음')
        return jsonify('1')

    #new user insert try
    data = user_schema.dictionalize()
    cnt,db_check = dbman.check_sign_in(data)
    if db_check:#중복회원가입 등, request<->DB간 consistency check 완료
        new_user_id = dbman.insert_sign_in(data)
        print('{} 가입완료'.format(data['name']))
        return jsonify('0')
    else:
        if cnt == '3':
            print('[회원가입]이름-전화번호 중복')
            return jsonify('3')
        if cnt == '2':
            print('[회원가입]ID중복')
            return jsonify('2')
            

@application.route('/login',methods=['POST'])
def login():
    print('[로그인 요청]')
    print(request.form)
    
    #input data check
    login_schema = Login_schema(request.form)
    if login_schema.empty_error:
        return jsonify('1')
    if login_schema.error or login_schema.missing:
        print('LOGIN ERROR')
        return jsonify('1')

    #try to login
    data = login_schema.dictionalize()
    num,login_result,user_type = dbman.try_login(data)
    if login_result:#success login
        print('로그인 성공')
        print(user_type)
        if user_type == 'Seller':
            print('4')
            return jsonify('4')
        if user_type == 'Purchaser':
            print('0')
            return jsonify('0')
        else:
            print("꺄울~")
    else:#fail to login
        print('로그인 실패')
        return jsonify(num)#2=ID없음 3=비밀번호틀림

@application.route('/foodtruck_location',methods=['POST'])
def foodtruck_location():
    id_ = request.form['id']
    loc = dbman.foodtruck_location(id_)
    return jsonify('0',{'lat':loc[0],'lng':loc[1]})
    
@application.route('/foodtruck_enroll',methods=['POST'])
def foodtruck_enroll():
    assert(request.method == 'POST')

    #하나의 도메인이 여러 기능을 하고, 각 기능은 input key의 개수를 통해 판단한다.
    if len(list(request.form.keys())) != 1: #푸드드럭 등록
        print('[푸드트럭 가입 혹은 수정 요청]')
        
        #input data check
        fd_enroll_schema = Foodtruck_enroll_schema(request.form)
        if fd_enroll_schema.area_error:
            return jsonify('2')
        if fd_enroll_schema.error:
            return jsonify('3')
        if fd_enroll_schema.category_error:
            return jsonify('4')
        if fd_enroll_schema.photo_error:
            return jsonify('5')

        data = fd_enroll_schema.dictionalize()
        #2. db duplicate check(food truck name)
        db_check= dbman.check_foodtruck_enroll(data)
        '''
        db_check
        None : 해당 유저의 아이디로 등록된 푸드트럭이 있음
        False : 동일한 데이터(ex:매장번호)로 등록된 매장이 있음
        True : OK
        '''
        if db_check == None:#푸드트럭 수정 요청 
            res = dbman.modify_foodtruck(data)
            return jsonify('0')
        elif not db_check:#중복유저
            return jsonify('1')

        insert_res = dbman.insert_foodtruck_enroll(data)   
        print('푸드트럭 등록 완료')
        return jsonify('0')

    else:#'나의 푸드트럭 클릭. 이미 있으면 채우고, 없으면 -1로 채움'
        user_id = request.form['id']
        error,my_foodtruck_data = dbman.find_foodtruck_info(user_id)
        if str(error)=='-1' :print('유저의 푸드트럭이 존재하지 않음')
        print('나의 푸드트럭 결과 반환')
        return jsonify(str(error),my_foodtruck_data)

@application.route('/menu_enroll',methods=['POST'])
def menu_enroll():
    print('[메뉴등록 요청]') 
    schem = Menu_schema(request.form)
    data = schem.dictionalize()
    if schem.empty_error:
        return jsonify('2')#빈값
    db_status = dbman.menu_enroll(data)
    if db_status:
        existing_menu = dbman.find_menulist_of_user(data['id'])
        print('메뉴 등록 완료')
        return jsonify('0',{'menulist':existing_menu})
    return jsonify('1')

@application.route('/sale_state',methods=['POST'])
def start_sale():
    print('[판매 여부 변경 요청]')
    raw_data = dict()
    raw_data['id'] = request.form['id']
    tmp = eval(request.form['location'])
    raw_data['location'] = (float(tmp[0]),float(tmp[1]))
    start_end = request.form['status']
    if start_end == '1':#판매시작
        status,menulist = dbman.start_sale(raw_data)
        if status == -1:#푸드트럭 없는 사람이 장사 종료
            return jsonify('-1',{'menulist':[]})
        print('메뉴 리스트 : ',end='')
        print(menulist)
        if status:
            print('시작')
            return jsonify('1',{'menulist':menulist})
    if start_end =='0':#판매종료
        raw_data['total_price'] = request.form['total_price']
        status = dbman.end_sale(raw_data)
        if status:
            print('종료')
            return jsonify('0')
    return jsonify('-1')

@application.route('/review_write',methods=['POST'])
def review_write():
    print('[리뷰 작성]')
    print(request.form)
    rw_schem = Review_schema(request.form)
    if rw_schem.empty_error:
        print('[빈 값]')
        return jsonify('1')

    schem = rw_schem.dictionalize()
    allreview = dbman.review_write(schem)
    print('리뷰작성완료')
    return jsonify('0',{'reviewlist':allreview})
    
@application.route('/menu_remove',methods=['POST'])
def menu_remove():
    print('[메뉴 삭제]')
    print(request.form)
    res = dbman.remove_menu(request.form)
    return jsonify('0')

@application.route('/search',methods=['POST'])
def search():
    print('[검색 요청]')
    print(request.form)
    search_schema = Search_schema(request.form)
    conditions = search_schema.dictionalize()
    search_result = dbman.search_foodtruck(conditions)
    print('검색 완료')
    for idx,i in enumerate(search_result[1]):
        search_result[1][idx]['photo'] ='하하하하하하하하하하하하하하'
    data = jsonify(search_result[0],{'data':search_result[1]})
    return data
    
@application.route('/foodtruck_page',methods=['POST'])
def foodtruck_page():
    '''
    푸드트럭 소유자의 id를 받으면, 해당 푸드트럭 정보 return
    푸드트럭 검색 이후, 푸드트럭 검색에서 사용된다.
    '''
    print('[푸드트럭 조회]')
    owner_id = request.form['id']
    fd_search_result = dbman.find_foodtruck_info(owner_id)#푸드트럭 정보
    menu_result = None#해당 푸드트럭의 메뉴 리스트
    fd_search_result['menu'] = menu_result
    return jsonify('0',search_result)
    
@application.route('/sale_list',methods=['POST'])
def sale_list():
    print('[판매정보 조회]')
    user_id = request.form['id']
    sales_result = dbman.fd_sale_list(user_id)
    return jsonify('0',{'salelist':sales_result})

@application.route('/fd_photo',methods=['POST'])
def fd_photo():
    print('[푸드트럭 사진 정보 요청]')
    user_id = request.form['f_id']
    photo = dbman.find_photo(user_id)
    print(photo[:10])
    return jsonify('0',{'photo':photo})

@application.route('/keyword_recommend',methods=['POST'])
def keyword_recommend():
    print('[검색 키워드 추천]')
    raw_loc = request.form['location']
    location = (float(raw_loc.split(',')[0][1:]),float(raw_loc.split(',')[1][:-1]))
    keyword = dbman.recommend_keyword(location)
    return jsonify('0',{'keyword':keyword})

if __name__ == '__main__':
    ip='0.0.0.0'
    port = 8081
    application.run(host=ip,port=port,debug=True,use_reloader=False)
    


