import os
import requests
from datetime import datetime, timedelta
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont # 이미지 생성을 위한 라이브러리

# 1. 학교 설정 (여기에 본인 학교 정보를 입력하세요!)
ATPT_OFCDC_SC_CODE = "Q10" # 예: "B10" (서울)
SD_SCHUL_CODE = "8490081"      # 예: "7011000"

# 폰트 경로 설정 (GitHub Actions 환경에 기본으로 설치된 폰트 사용)
# 대부분의 Linux 환경에서 사용 가능한 한글 폰트입니다.
FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" 

# 2. 급식 정보 가져오기 함수
def get_diet():
    # 내일 날짜 구하기
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    
    # 나이스 API 주소
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={tomorrow}"
    
    response = requests.get(url).json()
    
    try:
        # 급식 메뉴 텍스트 정리
        menu = response['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        menu = menu.replace("<br/>", "\n") # 줄바꿈 정리
        return f"내일의 급식 메뉴 ({tomorrow})\n\n{menu}"
    except (KeyError, IndexError): # 정보가 없거나 에러 발생 시
        return None

# 3. 이미지 생성 함수
def create_meal_image(text_content, image_path="meal_image.jpg"):
    img_width, img_height = 1080, 1080 # 인스타그램 표준 비율
    img = Image.new('RGB', (img_width, img_height), color = (0, 0, 0)) # 검정 배경
    d = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 40) # 폰트 크기 40
    except IOError:
        print(f"폰트 파일을 찾을 수 없습니다: {FONT_PATH}. 기본 폰트 사용.")
        font = ImageFont.load_default() # 기본 폰트 로드 (한글 깨질 수 있음)

    # 텍스트가 이미지 중앙에 오도록 계산
    lines = text_content.split('\n')
    line_height = d.textbbox((0,0), "테스트", font=font)[3] - d.textbbox((0,0), "테스트", font=font)[1] # 텍스트 한 줄 높이
    total_text_height = len(lines) * line_height
    
    y_text = (img_height - total_text_height) / 2 # 시작 y 좌표

    for line in lines:
        text_bbox = d.textbbox((0,0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_text = (img_width - text_width) / 2
        d.text((x_text, y_text), line, font=font, fill=(255, 255, 255)) # 흰색 글씨
        y_text += line_height # 다음 줄로 이동

    img.save(image_path)
    return image_path

# 4. 인스타그램 봇 실행 로직
USER_ID = os.environ.get("INSTA_ID")
USER_PW = os.environ.get("INSTA_PW")

diet_text = get_diet()

if diet_text:
    print("급식 정보 가져오기 성공!")
    print(diet_text)
    
    # 이미지 생성
    image_file = create_meal_image(diet_text)
    print(f"급식 이미지 생성 완료: {image_file}")

    # 인스타그램 업로드
    cl = Client()
    try:
        cl.login(USER_ID, USER_PW)
        cl.photo_upload(image_file, f"🥗 {datetime.now().strftime('%Y년 %m월 %d일')} 내일 급식 메뉴입니다!\n\n#급식 #급식메뉴 #학교급식")
        print("인스타그램 게시물 업로드 성공!")
    except Exception as e:
        print(f"인스타그램 업로드 실패: {e}")
else:
    print("내일 급식 정보가 없거나 가져오는데 실패했습니다.")

