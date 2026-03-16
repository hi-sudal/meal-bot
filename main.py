import os
import requests
import time
import json
from datetime import datetime, timedelta
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

# --- 학교 설정 (본인 정보 입력) ---
ATPT_OFCDC_SC_CODE = "Q10" 
SD_SCHUL_CODE = "8490081"
# -------------------------------

FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" 
SESSION_FILE = "session.json" # 세션 정보를 저장할 파일명

def get_diet_all():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={tomorrow}"
    response = requests.get(url).json()
    meals = {"조식": "", "중식": "", "석식": ""}
    try:
        rows = response['mealServiceDietInfo'][1]['row']
        for row in rows:
            meal_type = row['MMEAL_SC_NM']
            menu = row['DDISH_NM'].replace("<br/>", "\n")
            if meal_type in meals: meals[meal_type] = menu
        return tomorrow, meals
    except: return tomorrow, None

def create_meal_image(date_str, meal_type, menu_text, file_name):
    img = Image.new('RGB', (1080, 1080), color = (26, 26, 26))
    d = ImageDraw.Draw(img)
    try:
        font_main = ImageFont.truetype(FONT_PATH, 55)
        font_title = ImageFont.truetype(FONT_PATH, 65)
        font_footer = ImageFont.truetype(FONT_PATH, 40)
    except: font_main = font_title = font_footer = ImageFont.load_default()

    date_dt = datetime.strptime(date_str, '%Y%m%d')
    display_date = f"{date_dt.month}월 {date_dt.day}일"
    d.text((80, 80), f"{display_date} [{meal_type}]", font=font_title, fill=(255, 255, 255))
    d.text((80, 250), menu_text, font=font_main, fill=(255, 255, 255), spacing=20)
    d.text((80, 920), date_dt.strftime('%Y.%m.%d'), font=font_footer, fill=(200, 200, 200))
    img.save(file_name)

# 실행 로직
USER_ID = os.environ.get("INSTA_ID")
USER_PW = os.environ.get("INSTA_PW")
date_str, meal_data = get_diet_all()

if meal_data:
    image_paths = [f"{m_type}.jpg" for m_type, m_menu in meal_data.items() if m_menu]
    for m_type, m_menu in meal_data.items():
        if m_menu: create_meal_image(date_str, m_type, m_menu, f"{m_type}.jpg")
    
    if image_paths:
        cl = Client()
        try:
            # 1. 기존 세션이 있다면 로드
            if os.path.exists(SESSION_FILE):
                cl.load_settings(SESSION_FILE)
                print("기존 세션을 불러왔습니다.")
            
            time.sleep(3)
            cl.login(USER_ID, USER_PW)
            
            # 2. 로그인 성공 후 세션 저장
            cl.dump_settings(SESSION_FILE)
            print("로그인 성공 및 세션 저장 완료!")
            
            cl.album_upload(image_paths, caption=f"🥗 {date_str} 오늘의 급식 메뉴입니다!")
        except Exception as e:
            print(f"오류 발생: {e}")
