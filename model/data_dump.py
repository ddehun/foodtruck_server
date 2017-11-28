#dumping_app_data
import requests
from pymongo import MongoClient

if __name__ == '__main__':
    ip = 'http://143.248.199.114:8081/'
    #1. 유저 회원가입
    sign_in_key = ['id','password','name','phone','type']
    sign_in_data = []
    sign_in_data.append(['ddehun','1234','박채훈','01041843361','Purchaser'])
    sign_in_data.append(['JAMM','1234','이지호','01041843362','Purchaser'])
    sign_in_data.append(['star56','1234','윤상일','01041843363','Purchaser'])
    sign_in_data.append(['Faker','1234','이상혁','01041843364','Purchaser'])
    sign_in_data.append(['Pray','1234','김종인','01041843365','Purchaser'])
    sign_in_data.append(['Trevi','1234','신상민','01041843366','Seller'])
    sign_in_data.append(['Lemon','1234','이재후','01041843367','Seller'])
    sign_in_data.append(['Alcoholic','1234','류지일','01041843368','Seller'])
    sign_in_data.append(['trump','1234','김혜리','01041843369','Seller'])
    sign_in_data.append(['Mr.Baek','1234','백종원','01041843360','Seller'])
    sign_in_data.append(['Dopa', '1234', '이혁재', '01012345232', 'Seller'])
    sign_in_data.append(['peanut', '1234', '한왕호', '01015411234', 'Seller'])
    sign_in_data.append(['haemul', '1234', '이한별', '01012123456', 'Seller'])
    for i in sign_in_data:
        tmp = dict()
        for el,k in zip(i,sign_in_key):
            tmp[k]=el
        res = requests.post(ip+'sign_in',data=tmp)
        print(res)

    #2. 푸드트럭 회원가입
    ft_enroll_key = ['id','name','phone','area','ctg','introduction','photo']
    ft_enroll_data = []
    cl = MongoClient('localhost',27017)
    db=cl.test
    photo_str = db.foodtruck.find_one({'id':'seller1'})['photo']
    lat,long = db.foodtruck.find_one({'id':'seller1'})['lat'],db.foodtruck.find_one({'id':'seller1'})['long']

    ft_enroll_data.append(['Trevi','오늘의 에이드','0423501253','4','11','지친 일상, 짜릿한 에이드 한잔으로 하루를 시작해보세요!',photo_str])
    ft_enroll_data.append(['Lemon', '눈물젖은 닭강정', '0423503453', '4', '4', '닭강정을 전문으로 판매하는 푸드트럭입니다.', photo_str])
    ft_enroll_data.append(['Alcoholic', '후끈화끈치킨데이', '0423507767', '4', '4', '화끈한 치킨, 뜨거운 일탈!', photo_str])
    ft_enroll_data.append(['trump', '베트남사나이', '0423509899', '4', '6', '25년 전통 베트남 쌀국수집에서 전수받은 베트남 요리의 진수를 보여드립니다.ㅏ', photo_str])
    ft_enroll_data.append(['Mr.Baek', '너에게 꼬치다', '0423509383', '4', '1', '꼬치요리를 전문으로 판매하는 푸드트럭입니다', photo_str])
    ft_enroll_data.append(['Dopa', '이선생표 핫도그', '0422431123', '4', '8', '바쁜 하루, 핫도그 하나로 든든한 식사를~', photo_str])
    ft_enroll_data.append(['peanut', '왕호네 피자가게', '0423500984', '4', '3', '왕호의 푸드트럭에 어서오세요!', photo_str])
    ft_enroll_data.append(['haemul', '한별이의 해물레시피', '0423506676', '4', '12', '해물과 푸드트럭의 절묘한 조화!', photo_str])

    for i in ft_enroll_data:
        tmp = dict()
        for el,k in zip(i,ft_enroll_key):
            tmp[k]=el
        res = requests.post(ip+'foodtruck_enroll', data=tmp)
        print(res)

    #3. 푸드트럭들을, 현재 판매중이라구 하장.
    start_sale_key = ['id','location','status']
    start_sale_data = []
    start_sale_data.append(['Trevi', '({},{})'.format(lat - 0.005, long), '1'])
    start_sale_data.append(['Lemon', '({},{})'.format(lat - 0.004, long), '1'])
    start_sale_data.append(['Alcoholic', '({},{})'.format(lat - 0.001, long), '1'])
    start_sale_data.append(['trump', '({},{})'.format(lat - 0.003, long), '1'])
    start_sale_data.append(['Mr.Baek', '({},{})'.format(lat, long - 0.007), '1'])
    start_sale_data.append(['Dopa', '({},{})'.format(lat, long - 0.014), '1'])
    start_sale_data.append(['peanut', '({},{})'.format(lat, long - 0.013), '1'])
    start_sale_data.append(['haemul', '({},{})'.format(lat, long - 0.012), '1'])

    for i in start_sale_data:
        tmp = dict()
        for el,k in zip(i,start_sale_key):
            tmp[k]=el
        res = requests.post(ip+'sale_state', data=tmp)
        print(res)

    #4. 현재 판매중인 애들을 종료시킨다.
    start_sale_key = ['id','location','status','total_price']
    start_sale_data = []
    start_sale_data.append(['Trevi', '({},{})'.format(lat - 0.005, long), '0','100000'])
    start_sale_data.append(['Lemon', '({},{})'.format(lat - 0.004, long), '0','254000'])
    start_sale_data.append(['Alcoholic', '({},{})'.format(lat - 0.001, long), '0','560000'])
    start_sale_data.append(['trump', '({},{})'.format(lat - 0.003, long), '0','86400'])
    start_sale_data.append(['Mr.Baek', '({},{})'.format(lat, long-0.007), '0','124300'])
    start_sale_data.append(['Dopa', '({},{})'.format(lat, long - 0.014), '0','490000'])
    start_sale_data.append(['peanut', '({},{})'.format(lat, long-0.013), '0','124300'])
    start_sale_data.append(['haemul', '({},{})'.format(lat, long - 0.012), '0','490000'])

    for i in start_sale_data:
        tmp = dict()
        for el,k in zip(i,start_sale_key):
            tmp[k]=el
        res = requests.post(ip+'sale_state', data=tmp)
        print(res)

    #5. 메뉴 등록
    menu_enroll_keys = ['id','name','price','ingredients']
    menu_data = []
    menu_data.append(['Trevi', '자몽 에이드', '3000', '자몽,사이다,물,설탕'])
    menu_data.append(['Trevi', '유자 에이드', '3500', '유자,사이다,물,설탕'])
    menu_data.append(['Trevi', '레몬 에이드', '2500', '레몬,레몬즙,사이다,물,설탕'])
    menu_data.append(['Trevi', '녹차 에이드', '3000', '녹차,사이다,물,설탕'])
    menu_data.append(['Trevi', '사과 에이드', '3000', '사과,사이다,물,설탕'])
    menu_data.append(['Lemon', '닭강정 (Small)', '3000', '닭,설탕,마늘,깨,호두,고춧가루,식용유,후추'])
    menu_data.append(['Lemon', '닭강정 (Normal)', '4000', '닭,설탕,마늘,깨,호두,고춧가루,식용유,후추'])
    menu_data.append(['Lemon', '닭강정 (Large)', '5000', '닭,설탕,마늘,깨,호두,고춧가루,식용유,후추'])
    menu_data.append(['Lemon', '눈물나는 닭강정', '4000', '청양고추,닭,설탕,마늘,깨,호두,고춧가루,식용유,후추'])
    menu_data.append(['Lemon', '콜팝', '2500', '닭,설탕,마늘,깨,호두,고춧가루,식용유,후추','콜팝'])
    menu_data.append(['Lemon', '순한맛 닭강정', '4000', '우유,닭,설탕,마늘,깨,호두,고춧가루,식용유,후추'])
    menu_data.append(['Alcoholic', '매운 치킨', '4000', '닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['Alcoholic', '더매운 치킨', '4000', '닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['Alcoholic', '평범한 치킨', '4000', '닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['Alcoholic', '매운 닭강정', '2000', '닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['Alcoholic', '치킨 샐러드', '3000', '양배추,마늘,닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['Alcoholic', '크림 치킨', '4000', '우유,닭,고춧가루,밀가루,식용유,소금,설탕,청양고추'])
    menu_data.append(['trump', '팟타이', '4000', '소면,밀가루,기름,새우,설탕,후추,소금,우유,버섯'])
    menu_data.append(['trump', '쌀국수', '3500', '멸치,소면,밀가루,기름,설탕,버섯'])
    menu_data.append(['Mr.Baek', '닭꼬치', '2500', '닭,고춧가루,기름,후추,마늘,소금'])
    menu_data.append(['Mr.Baek', '양꼬치', '3500', '양,소주,고춧가루,기름,후추,마늘,소금'])
    menu_data.append(['Mr.Baek', '소세지 모둠 꼬치', '300', '소세지,고춧가루,기름,후추,마늘,소금'])
    menu_data.append(['Dopa', '핫커리핫도그', '3500', '고춧가루,강황,카레가루,감자,햄,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['Dopa', '전통핫도그', '3500', '햄,김치,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['Dopa', '퓨전핫도그', '3000', '햄,소고기,우유,소면,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['Dopa', '일반핫도그', '2500', '햄,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['peanut', '베이컨피자', '3000', '베이컨,야채,햄,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['peanut', '고구마피자', '3000', '고구마,햄,야채,햄,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['peanut', '김치피자', '3000', '김치,베이컨,야채,햄,밀가루,튀김가루,설탕,소금,베이킹소다'])
    menu_data.append(['haemul', '오징어구이', '2000', '손질된오징어,기름,소금,후추,간장'])
    menu_data.append(['haemul', '연어회샐러드', '4000', '연어,샐러드드레싱,야채,간장,와사비'])
    menu_data.append(['haemul', '조개구이', '3500', '조개,간장,와사비,기름,후추,소금'])

    for i in menu_data:
        tmp = dict()
        for el,k in zip(i,menu_enroll_keys):
            tmp[k]=el
        res = requests.post(ip+'menu_enroll', data=tmp)
        print(res)

    #6. 리뷰 등록
    review_key = ['ft_id','w_id','rating','detail']
    review_data = []
    review_data.append(['Trevi', 'ddehun', '4', '에이드 완전 맛있어요!!'])
    review_data.append(['Trevi', 'JAMM', '2', '금방 된다고 하시더니,,,,, 30분이나 기다렸네요.....OTLL....'])

    review_data.append(['Trevi', 'star56', '5', '친절한 주인 아저씨 덕분에 기분 UP!!!!'])
    review_data.append(['Trevi', 'Faker', '5', 'Oh my god... your drink is really Wonderful... I lov it ><'])
    review_data.append(['Trevi', 'Pray', '1', '자몽에이드 달라구 했는데 녹차에이드 주심 ㅡㅡ'])
    ft_id = 'Lemon'
    review_data.append([ft_id, 'ddehun', '5', '이 닭강정을 먹고 암이 나았습니다.'])
    review_data.append([ft_id, 'JAMM', '2', '1분만에 된다고 하시더니,,,,, 30분이나 기다렸네요.....OTLL....'])
    review_data.append([ft_id, 'star56', '5', '무서운 아저씨인줄만 알았는데, 정말루다가 무서웠습니다.'])
    review_data.append([ft_id, 'Faker', '5', '닭.....좋아.....'])
    review_data.append([ft_id, 'Faker', '4', '이 닭강정을 먹고 롤을 했더니 우승을 했습니다.'])
    review_data.append([ft_id, 'Pray', '1', '닭강정이 눈물에 젖다니,,,, 비위생적이네요....'])
    ft_id = 'Alcoholic'
    review_data.append([ft_id, 'ddehun', '5', '치킨 맛있쪙.'])
    review_data.append([ft_id, 'ddehun', '5', '이 치킨을 먹고 수능 100점을 맞았습니다.'])
    review_data.append([ft_id, 'JAMM', '5', '1분만에 된다고 하시더니,,,,, 정말 1분만에 만들어주셨네요.'])
    review_data.append([ft_id, 'star56', '5', '치킨 완전 맛있어요! 갓 튀긴 치킨의 그 육즙이란.......'])
    review_data.append([ft_id, 'Faker', '5', '화끈화끈한 맛이지만, 너무 맛있어서 다 먹어버렸어요! 다음에 또 먹으러 오려구요ㅎㅎㅎ'])
    review_data.append([ft_id, 'Faker', '4', '너무너무 맛있는 맛이에요!'])
    ft_id = 'trump'
    review_data.append([ft_id, 'ddehun', '5', '아, 당신이 바로 베트남의 고든 렘지입니까?'])
    review_data.append([ft_id, 'JAMM', '4', '쌀국수를  처음 먹어봤는데, 완전 맛있네요ㅎㅎ'])
    review_data.append([ft_id, 'star56', '5', '그의 음식을 한입 베어문 순간, 나는 이곳이 베트남임을 믿어 의심치 않았다.'])
    review_data.append([ft_id, 'Faker', '1', '먹을만하긴 한데, 너무 오래걸리네요ㅠ-ㅠ'])
    review_data.append([ft_id, 'Faker', '4', '맛있어요!'])

    for i in review_data:
        tmp = dict()
        for el,k in zip(i,review_key):
            tmp[k]=el
        res = requests.post(ip+'review_write', data=tmp)
        print(res)


    '''
    
    ft_enroll_data.append(['Mr.Baek', '너에게 꼬치다', '0423509383', '4', '1', '꼬치요리를 전문으로 판매하는 푸드트럭입니다', photo_str])
    Dopa
    peanut
    haemul
    '''