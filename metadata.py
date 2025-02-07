import os
import json
import subprocess

def extract_metadata(image_path):
    """exiftool을 사용하여 이미지 메타데이터를 추출"""
    try:
        # exiftool 설치 확인
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ exiftool이 설치되어 있지 않습니다.")
        print("Ubuntu/Debian: sudo apt-get install exiftool")
        print("Mac: brew install exiftool")
        return None

    try:
        result = subprocess.run(
            ["exiftool", "-json", image_path],
            capture_output=True,
            text=True,
            check=True
        )
        metadata = json.loads(result.stdout)
        return metadata[0] if metadata else None
    except subprocess.CalledProcessError as e:
        print(f"메타데이터 추출 실패: {image_path} - {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 변환 실패: {image_path} - {e}")
        return None

def process_metadata(image_folder="static/results", metadata_folder="static/results/metadata"):
    """모든 이미지 파일의 메타데이터를 JSON 파일로 저장"""
    # 폴더가 없으면 생성 (상위 폴더도 함께 생성)
    os.makedirs(metadata_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)

    image_files = [
        f for f in os.listdir(image_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"))
        and os.path.isfile(os.path.join(image_folder, f))  # 파일인지 확인
    ]

    print(f"발견된 이미지 파일 수: {len(image_files)}")
    
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        metadata = extract_metadata(image_path)
        if metadata:
            metadata_path = os.path.join(metadata_folder, f"{os.path.splitext(image_file)[0]}.json")
            with open(metadata_path, "w", encoding="utf-8") as json_file:
                json.dump(metadata, json_file, ensure_ascii=False, indent=4)
            print(f"메타데이터 저장 완료: {metadata_path}")
        else:
            print(f"메타데이터 추출 실패: {image_path}")

if __name__ == "__main__":
    process_metadata()