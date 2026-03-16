from instagrapi import Client
import os

# 나중에 깃허브 보안 설정(Secrets)에 넣을 값들입니다.
USER_ID = os.environ.get("INSTA_ID")
USER_PW = os.environ.get("INSTA_PW")

cl = Client()

try:
    cl.login(USER_ID, USER_PW)
    print("로그인 성공!")
    # 여기에 나중에 급식 사진을 올리는 코드를 추가할 거예요.
except Exception as e:
    print(f"로그인 실패: {e}")
