# 여행콕 (TravelCock)

한국관광공사 국문 관광정보 서비스(KorService2)를 활용한 국내 관광지 검색 웹사이트입니다.

## 실행

1. Python 가상환경을 활성화합니다.
2. 의존성을 설치합니다: `pip install -r requirements.txt`
3. `TOUR_API_KEY` 환경변수에 한국관광공사 API 인증키를 설정합니다.
4. 실행합니다: `python app.py`

## Render 배포

이 저장소를 Render의 Web Service로 연결하면 `render.yaml` 설정을 사용할 수 있습니다.

Render 서비스의 Environment에 다음 환경변수를 등록하세요.

- `TOUR_API_KEY`: 한국관광공사 API 인증키

인증키는 GitHub 코드나 공개 파일에 넣지 마세요.
