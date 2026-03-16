import os
import requests
import time
from datetime import datetime, timedelta
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

# 1. 학교 설정 (본인 학교 정보 입력)
ATPT_OFCDC_SC_CODE = "Q10" 
SD_SCHUL_CODE = "8490081"

FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" 

def get_diet_all():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    # 나이스 API는 MMEAL_SC_CODE를 지정하지 않으면 해당 날짜의 모든 급식을 가져옵니다.
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={tomorrow}"
    
    response = requests.get(url).json()
    meals = {"조식": "", "중식": "", "석식": ""}
    
    try:
        rows = response['mealServiceDietInfo'][1]['row']
        for row in rows:
            meal_type = row['MMEAL_SC_NM'] # 조식, 중식, 석식 등
            menu = row['DDISH_NM'].replace("<br/>", "\n")
            if meal_type in meals:
                meals[meal_type] = menu
        return tomorrow, meals
    except (KeyError, IndexError):
        return tomorrow, None

def create_meal_image(date_str, meal_type, menu_text, file_name):
    # 사진 배경 및 크기 설정 (1080x1080 검은색)
    img = Image.new('RGB', (1080, 1080), color = (26, 26, 26)) # 완전 검정보다 살짝 부드러운 검정
    d = ImageDraw.Draw(img)
    
    try:
        font_main = ImageFont.truetype(FONT_PATH, 55) # 메뉴 폰트
        font_title = ImageFont.truetype(FONT_PATH, 65) # 상단 날짜 폰트
        font_footer = ImageFont.truetype(FONT_PATH, 40) # 하단 날짜 폰트
    except IOError:
        font_main = font_title = font_footer = ImageFont.load_default()

    # 날짜 포맷팅 (예: 2월 2일)
    date_dt = datetime.strptime(date_str, '%Y%m%d')
    display_date = f"{date_dt.month}월 {date_dt.day}일"
    
    # [1] 상단 제목: 2월 2일 [조식]
    d.text((80, 80), f"{display_date} [{meal_type}]", font=font_title, fill=(255, 255, 255))
    
    # [2] 중앙 메뉴 (왼쪽 정렬)
    d.text((80, 250), menu_text, font=font_main, fill=(255, 255, 255), spacing=20)
    
    # [3] 하단 날짜: 2026.02.02
    footer_date = date_dt.strftime('%Y.%m.%d')
    d.text((80, 920), footer_date, font=font_footer, fill=(200, 200, 200))

    img.save(file_name)
    return file_name

# 실행 로직
USER_ID = os.environ.get("INSTA_ID")
USER_PW = os.environ.get("INSTA_PW")

date_str, meal_data = get_diet_all()

if meal_data:
    image_paths = []
    # 데이터가 있는 급식만 이미지로 만듭니다.
    for m_type, m_menu in meal_data.items():
        if m_menu: # 메뉴가 비어있지 않은 경우만
            file_name = f"{m_type}.jpg"
            create_meal_image(date_str, m_type, m_menu, file_name)
            image_paths.append(file_name)
    
    if image_paths:
        cl = Client()
        try:
            time.sleep(3)
            cl.login(USER_ID, USER_PW)
            # 여러 장의 사진을 슬라이드로 업로드 (album_upload)
            cl.album_upload(
                image_paths,
                caption=f"🥗 {date_str} 오늘의 급식 메뉴입니다!"
            )
            print("슬라이드 게시물 업로드 성공!")
        except Exception as e:
            print(f"업로드 실패: {e}")
else:
    print("급식 데이터가 없습니다.")
