import download
import metadata
import subdomain
from crt_sh import get_subdomains
from domain_whois_analyze import analyze_domain

if __name__ == "__main__":
    url = input("이미지를 다운로드할 웹사이트 도메인을 입력하세요 (예: example.com): ").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url  # 기본적으로 HTTPS 사용

    domain = url.split("//")[-1]  # 프로토콜 제거 (예: "https://example.com" → "example.com")

    # 1. 서브도메인 정보 수집
    subdomains, subdomains_file = get_subdomains(domain)
    print(f"서브도메인 정보가 {subdomains_file}에 저장되었습니다.")

    # 2. WHOIS 정보 수집
    whois_info, whois_file = analyze_domain(domain)
    print(f"WHOIS 정보가 {whois_file}에 저장되었습니다.")

    # 3. 이미지 다운로드
    download.download_images(url, depth=2)

    # 4. 메타데이터 저장
    metadata.process_metadata()

