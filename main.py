import os
import requests
import time # 대기 시간을 위한 라이브러리
from datetime import datetime, timedelta
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

# 1. 학교 설정 (본인 학교 정보를 입력하세요)
ATPT_OFCDC_SC_CODE = "Q10" 
SD_SCHUL_CODE = "8490081"

FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" 

def get_diet():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={tomorrow}"
    response = requests.get(url).json()
    try:
        menu = response['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        menu = menu.replace("<br/>", "\n")
        return f"내일의 급식 메뉴 ({tomorrow})\n\n{menu}"
    except (KeyError, IndexError):
        return None

def create_meal_image(text_content, image_path="meal_image.jpg"):
    img = Image.new('RGB', (1080, 1080), color = (0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except IOError:
        font = ImageFont.load_default()

    lines = text_content.split('\n')
    y_text = 200 # 위쪽 여백
    for line in lines:
        d.text((100, y_text), line, font=font, fill=(255, 255, 255))
        y_text += 60
    img.save(image_path)
    return image_path

# 2. 실행 로직
USER_ID = os.environ.get("INSTA_ID")
USER_PW = os.environ.get("INSTA_PW")

diet_text = get_diet()

if diet_text:
    print("급식 정보 가져오기 성공!")
    image_file = create_meal_image(diet_text)
    
    cl = Client()
    try:
        # 로그인 전 3초 대기 (인스타 보안 우회 도움)
        print("인스타그램 로그인 준비 중... 3초간 대기합니다.")
        time.sleep(3) 
        
        print(f"로그인 시도 아이디: {USER_ID}")
        cl.login(USER_ID, USER_PW)
        
        print("로그인 성공! 업로드를 시작합니다.")
        cl.photo_upload(image_file, f"🥗 {datetime.now().strftime('%Y-%m-%d')} 내일의 급식 메뉴!")
        print("게시물 업로드 완료!")
    except Exception as e:
        print(f"로그인 또는 업로드 중 에러 발생: {e}")
else:
    print("내일 급식 정보가 없습니다.")
