import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# SSL 경고 메시지 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

visited_urls = set()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.google.com/",
}

def normalize_url(url):
    """URL이 http:// 또는 https:// 없으면 자동 추가"""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url  # 기본적으로 HTTPS 사용
    return url

def download_images(url, folder="static/results", depth=2, session=None):
    """웹페이지에서 이미지를 다운로드하고 내부 페이지도 재귀적으로 탐색"""
    global visited_urls

    url = normalize_url(url)
    if url in visited_urls or depth < 0:
        return
    visited_urls.add(url)

    print(f"크롤링 중: {url} (남은 깊이: {depth})")

    # 폴더가 없으면 생성 (상위 폴더도 함께 생성)
    os.makedirs(folder, exist_ok=True)

    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)

    try:
        response = session.get(url, timeout=5, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"웹 요청 실패: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    img_tags = soup.find_all("img")
    count = 0

    for img in img_tags:
        img_url = img.get("src")
        if not img_url:
            continue

        img_url = urljoin(url, img_url)
        try:
            ext = os.path.splitext(img_url)[-1].lower()
            if ext not in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                ext = ".jpg"

            img_path = os.path.join(folder, f"image_{len(visited_urls)}_{count}{ext}")

            img_response = session.get(img_url, headers=HEADERS, timeout=5, verify=False)
            if img_response.status_code == 403:
                print(f"403 오류 발생, User-Agent 변경 후 재시도: {img_url}")
                img_response = session.get(img_url, headers={"User-Agent": "Googlebot"}, timeout=5, verify=False)

            if img_response.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(img_response.content)
                print(f"다운로드 완료: {img_path}")
                count += 1
            else:
                print(f"다운로드 실패 {img_url}: HTTP {img_response.status_code}")

        except Exception as e:
            print(f"다운로드 실패 {img_url}: {e}")

    links = soup.find_all("a", href=True)
    for link in links:
        next_page = urljoin(url, link["href"])
        parsed_url = urlparse(next_page)

        if parsed_url.netloc == urlparse(url).netloc:
            download_images(next_page, folder, depth - 1, session)