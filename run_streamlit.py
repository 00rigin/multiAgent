#!/usr/bin/env python3
"""
Streamlit 채팅 앱 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    """Streamlit 앱을 실행합니다."""
    try:
        # 현재 디렉토리 확인
        current_dir = os.getcwd()
        print(f"현재 디렉토리: {current_dir}")
        
        # Streamlit 앱 실행
        print("🚀 Streamlit 채팅 앱을 시작합니다...")
        print("📱 브라우저에서 http://localhost:8501 을 열어주세요")
        print("⚠️  API 서버(localhost:8000)가 실행 중인지 확인해주세요")
        print("-" * 50)
        
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/streamlit_chat.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Streamlit 앱이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 다음을 확인해주세요:")
        print("   1. streamlit이 설치되어 있는지: pip install streamlit")
        print("   2. API 서버가 실행 중인지: python -m uvicorn app.main:app --reload")
        print("   3. 필요한 패키지들이 설치되어 있는지: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 