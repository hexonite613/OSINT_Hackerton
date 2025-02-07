import requests
import json
import os

def get_subdomains(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        print(f"요청 URL: {url}")  # 디버깅용 출력
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 오류 확인
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {str(e)}")
            print(f"응답 내용: {response.text[:200]}")  # 응답 내용 일부 출력
            return []

        subdomains = sorted(set(entry["name_value"] for entry in data if "name_value" in entry))

        # JSON 파일 저장
        json_filename = f"static/results/{domain}_subdomains.json"
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(subdomains, json_file, indent=4, ensure_ascii=False)

        return subdomains, f"{domain}_subdomains.json"

    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {str(e)}")
        return []
    except Exception as e:
        print(f"기타 오류: {str(e)}")
        return [] 