from flask import Flask, render_template, request
import requests
import json
import os

TOUR_API_KEY = os.environ.get("TOUR_API_KEY", "").strip()

app = Flask(__name__)
BASE_URL = "https://apis.data.go.kr/B551011/KorService2"


def get_api_result(data):
    """공공데이터 API 응답에서 결과 코드, 메시지, 관광지 목록을 꺼낸다."""
    if not isinstance(data, dict):
        return None, None, []

    api_response = data.get("response")
    if not isinstance(api_response, dict):
        return data.get("resultCode"), data.get("resultMsg"), []

    header = api_response.get("header", {})
    body = api_response.get("body", {})
    if not isinstance(header, dict):
        header = {}
    if not isinstance(body, dict):
        body = {}

    result_code = header.get("resultCode")
    result_msg = header.get("resultMsg")
    items = body.get("items", {})
    places = items.get("item", []) if isinstance(items, dict) else []

    if isinstance(places, dict):
        places = [places]
    if not isinstance(places, list):
        places = []

    return result_code, result_msg, places


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    places = []
    error = None

    if not TOUR_API_KEY:
        error = "서버에 관광 API 인증키가 설정되지 않았습니다. 관리자에게 문의해 주세요."
        return render_template("index.html", places=places, error=error, search=search)

    if search:
        api_url = f"{BASE_URL}/searchKeyword2"
        params = {
            "serviceKey": TOUR_API_KEY,
            "numOfRows": 30,
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "TravelCock",
            "_type": "json",
            "arrange": "A",
            "keyword": search,
            "contentTypeId": "12"
        }
    else:
        api_url = f"{BASE_URL}/areaBasedList2"
        params = {
            "serviceKey": TOUR_API_KEY,
            "numOfRows": 30,
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "TravelCock",
            "_type": "json",
            "arrange": "A",
            "contentTypeId": "12"
        }

    try:
        response = requests.get(api_url, params=params, timeout=20)
        print("\nHTTP 상태 코드:", response.status_code)

        if response.status_code != 200:
            print("===== 서버 응답 본문 =====")
            print(response.text[:1000])
            print("==========================\n")

        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            print("===== JSON 변환 실패 =====")
            print(response.text[:2000])
            print("==========================\n")
            error = "API 응답이 JSON 형식이 아닙니다. 서버 로그를 확인해 주세요."
            data = None

        if data is not None:
            print("===== 공공데이터 API 응답 확인 =====")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
            print("====================================\n")

            result_code, result_msg, places = get_api_result(data)
            if result_code is None:
                error = "API 응답 구조를 확인할 수 없습니다. 서버 로그를 확인해 주세요."
            elif str(result_code) != "0000":
                error = f"API 오류: {result_code} - {result_msg}"
                places = []
            elif not places:
                error = "검색 결과가 없습니다. 다른 검색어를 입력해 보세요."

    except requests.exceptions.Timeout:
        error = "공공데이터 서버 응답 시간이 초과되었습니다."
    except requests.exceptions.HTTPError as e:
        print("HTTP 오류:", e)
        error = "공공데이터 서버에서 오류 응답을 보냈습니다. 서버 로그를 확인해 주세요."
    except requests.exceptions.RequestException as e:
        print("서버 연결 오류:", e)
        error = "공공데이터 서버에 연결할 수 없습니다."
    except Exception as e:
        print("예상하지 못한 오류:", e)
        error = "알 수 없는 오류가 발생했습니다."

    return render_template("index.html", places=places, error=error, search=search)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
