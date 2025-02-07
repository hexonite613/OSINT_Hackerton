from flask import Flask, render_template, request, jsonify, send_from_directory
from crt_sh import get_subdomains
import traceback  # 추가
from flask_wtf.csrf import CSRFProtect  # 추가
import os
import json
from domain_whois_analyze import analyze_domain, parse_domain_info  # 상단에 추가
from werkzeug.utils import secure_filename
import download  # 추가
import metadata  # 추가
import zipfile
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 보안을 위한 시크릿 키 설정
csrf = CSRFProtect(app)  # CSRF 보호 추가

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])  # GET 메소드도 허용
def search():
    try:
        if request.method == 'GET':
            return jsonify({'error': '잘못된 요청 방식입니다.'})
            
        domain = request.form.get('domain', '').strip()
        domain = domain.replace('https://', '').replace('http://', '')
        domain = domain.replace('www.', '')
        domain = domain.split('/')[0]
        
        if not domain:
            return jsonify({'error': '도메인을 입력해주세요'})
        
        print(f"검색하려는 도메인: {domain}")  # 디버깅용 출력
        
        url = f"https://{domain}"  # URL 생성
        
        # 1. 서브도메인 검색
        subdomains, json_filename = get_subdomains(domain)
        
        # 2. WHOIS 정보 분석
        whois_insights, whois_filename = analyze_domain(domain)
        
        # 3. 이미지 다운로드
        download.download_images(url, depth=0)
        
        # 4. 메타데이터 처리
        metadata.process_metadata()
        
        return jsonify({
            'subdomains': subdomains,
            'json_file': json_filename,
            'whois_insights': whois_insights,
            'whois_file': whois_filename,
            'message': '이미지 다운로드와 메타데이터 처리가 완료되었습니다.'
        })
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")  # 오류 내용 출력
        print(traceback.format_exc())  # 상세 오류 정보 출력
        return jsonify({'error': f'서버 오류가 발생했습니다: {str(e)}'})

# JSON 파일 다운로드를 위한 새로운 라우트 추가
@app.route('/download/<filename>')
def download_json(filename):
    try:
        return send_from_directory('static/results', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'파일 다운로드 중 오류 발생: {str(e)}'})

@app.route('/results/<filename>')
def show_results(filename):
    try:
        # 도메인 이름 추출 (파일명에서)
        domain = filename.replace('_subdomains.json', '')
        
        # 서브도메인 JSON 파일 경로
        json_path = os.path.join('static', 'results', filename)
        
        # WHOIS JSON 파일 경로
        whois_path = os.path.join('static', 'results', f"{domain}_whois.json")
        
        # 서브도메인 JSON 파일이 존재하는지 확인
        if not os.path.exists(json_path):
            return "결과 파일을 찾을 수 없습니다.", 404
            
        # JSON 파일 읽기
        with open(json_path, 'r', encoding='utf-8') as f:
            subdomains = json.load(f)
            
        # WHOIS 정보 읽기
        whois_insights = None
        if os.path.exists(whois_path):
            with open(whois_path, 'r', encoding='utf-8') as f:
                whois_data = json.load(f)
                whois_insights = parse_domain_info(whois_data)  # domain_whois_analyze.py의 함수 사용
            
        # 템플릿에 전달할 데이터 구성
        results = {
            'subdomains': subdomains,
            'json_file': filename,
            'domain': domain,
            'whois_insights': whois_insights,
            'whois_file': f"{domain}_whois.json"
        }
            
        return render_template('results.html', results=results, domain=domain)
    except Exception as e:
        print(f"Error: {str(e)}")  # 에러 로깅
        return f"오류가 발생했습니다: {str(e)}", 500

@app.route('/metadata/<filename>')
def show_metadata(filename):
    results_dir = os.path.join('static', 'results')
    metadata_dir = os.path.join(results_dir, 'metadata')
    
    # 이미지 파일 목록 가져오기
    images = []
    for img_file in os.listdir(results_dir):
        if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            metadata_file = os.path.join(metadata_dir, f"{os.path.splitext(img_file)[0]}.json")
            metadata = None
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            images.append({
                'filename': img_file,
                'metadata': metadata
            })
    
    return render_template('metadata.html', images=images)

@app.route('/download_all')
def download_all():
    # 메모리에 ZIP 파일 생성
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # results 폴더의 모든 파일을 압축
        results_dir = os.path.join('static', 'results')
        for root, dirs, files in os.walk(results_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, results_dir)
                zf.write(file_path, arcname)
    
    # 파일 포인터를 시작으로 되돌림
    memory_file.seek(0)
    
    return send_from_directory(
        directory='static/results',
        path='results.zip',
        as_attachment=True,
        download_name='results.zip'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # 5000 대신 8000 포트 사용 