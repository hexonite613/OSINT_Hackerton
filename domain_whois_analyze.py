import subprocess
import json
from datetime import datetime
import os

def run_whois(domain_name):
    """Run the whois command and return the result as text."""
    try:
        result = subprocess.run(["/usr/bin/whois", "-h", "whois.verisign-grs.com", domain_name],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Whois command failed: {result.stderr}")
        return result.stdout
    except FileNotFoundError:
        raise Exception("Whois command not found. Please install the whois package.")

def parse_whois_output(whois_output):
    """Parse the WHOIS output into a structured dictionary."""
    data = {}
    for line in whois_output.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
    return data

def parse_domain_info(domain_info):
    """Analyze and generate insights from the domain information."""
    insights = {}  # 딕셔너리로 변경하여 웹에서 더 쉽게 처리할 수 있도록 함
    today = datetime.today()

    # 도메인 이름 분석
    domain_name = domain_info.get("Domain Name", "Unknown")
    insights['domain_name'] = domain_name
    insights['domain_description'] = "이 도메인은 특정 서비스와 관련된 웹사이트로 추정할 수 있습니다."
    
    # 생성일 분석
    creation_date = domain_info.get("Creation Date")
    if creation_date:
        try:
            creation_date_obj = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            creation_date_obj = datetime.strptime(creation_date, "%Y-%m-%d")
        age = today.year - creation_date_obj.year
        insights['creation_date'] = creation_date
        insights['domain_age'] = f"약 {age}년 전에 등록된 도메인입니다."
    else:
        insights['creation_date'] = None
        insights['domain_age'] = "생성일 정보가 없습니다."

    # 갱신일 분석
    updated_date = domain_info.get("Updated Date")
    if updated_date:
        try:
            updated_date_obj = datetime.strptime(updated_date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            updated_date_obj = datetime.strptime(updated_date, "%Y-%m-%d")
        insights['updated_date'] = updated_date
        insights['update_status'] = "최근 갱신되었으며, 도메인을 지속적으로 관리 중임을 나타냅니다."
    else:
        insights['updated_date'] = None
        insights['update_status'] = "갱신일 정보가 없습니다."

    # 만료일 분석
    expiry_date = domain_info.get("Registry Expiry Date") or domain_info.get("Expiry Date")
    if expiry_date:
        try:
            expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
        days_to_expiry = (expiry_date_obj - today).days
        insights['expiry_date'] = expiry_date
        insights['expiry_status'] = f"도메인이 현재 활성 상태이며, 약 {days_to_expiry}일 후 만료될 예정입니다."
    else:
        insights['expiry_date'] = None
        insights['expiry_status'] = "만료일 정보가 없습니다."

    return insights

def analyze_domain(domain_name):
    """웹 애플리케이션에서 사용할 도메인 분석 함수"""
    try:
        whois_output = run_whois(domain_name)
        domain_info = parse_whois_output(whois_output)
        insights = parse_domain_info(domain_info)
        
        # JSON 저장
        json_filename = f"static/results/{domain_name}_whois.json"
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(domain_info, f, ensure_ascii=False, indent=4)
            
        return insights, f"{domain_name}_whois.json"
    except Exception as e:
        return {"error": str(e)}, None

def main():
    # 사용자 입력
    domain_name = input("도메인 이름을 입력하세요: ").strip()
    
    # WHOIS 실행 및 파싱
    print(f"'{domain_name}'에 대한 WHOIS 정보를 가져오는 중...")
    insights, json_filename = analyze_domain(domain_name)
    
    # WHOIS 정보 분석
    print("\n도메인 분석 결과:")
    for key, value in insights.items():
        print(f"{key}: {value}")

    print(f"\nWHOIS 데이터가 '{json_filename}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    main()