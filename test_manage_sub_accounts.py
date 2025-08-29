#!/usr/bin/env python3
"""
manage-sub-accounts 페이지 오류 디버깅 스크립트
"""

import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

def test_manage_sub_accounts_page():
    """manage-sub-accounts 페이지 오류 테스트"""
    
    print("=" * 60)
    print("🔍 manage-sub-accounts 페이지 오류 디버깅")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    try:
        # 1단계: 로그인 페이지 접근
        print("📱 1단계: 로그인 페이지 접근")
        login_url = "https://aptgo.org/login/"
        login_page = session.get(login_url)
        print(f"   ✅ 로그인 페이지 상태: {login_page.status_code}")
        
        # CSRF 토큰 추출
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print(f"   ✅ CSRF 토큰 획득: {csrf_value[:20]}...")
        else:
            print("   ❌ CSRF 토큰을 찾을 수 없음")
            return False
        
        # 2단계: 로그인 실행
        print("🔐 2단계: 사용자 로그인")
        login_data = {
            'username': 'newtest1754832743',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_value,
            'next': '/manage-sub-accounts/'
        }
        
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"   ✅ 로그인 응답 상태: {login_response.status_code}")
        
        if login_response.status_code == 302:
            redirect_location = login_response.headers.get('Location', '')
            print(f"   ✅ 리다이렉트 위치: {redirect_location}")
            
            # 리다이렉트 따라가기
            if redirect_location:
                if redirect_location.startswith('/'):
                    redirect_url = f"https://aptgo.org{redirect_location}"
                else:
                    redirect_url = redirect_location
                    
                redirect_response = session.get(redirect_url)
                print(f"   ✅ 리다이렉트 후 상태: {redirect_response.status_code}")
        
        # 3단계: manage-sub-accounts 페이지 직접 접근
        print("🔧 3단계: manage-sub-accounts 페이지 접근")
        target_url = "https://aptgo.org/manage-sub-accounts/"
        
        target_response = session.get(target_url)
        print(f"   📊 페이지 상태 코드: {target_response.status_code}")
        print(f"   📊 응답 크기: {len(target_response.content)} bytes")
        print(f"   📊 Content-Type: {target_response.headers.get('Content-Type', 'N/A')}")
        
        # 4단계: 응답 내용 분석
        print("🔍 4단계: 응답 내용 분석")
        
        if target_response.status_code == 200:
            soup = BeautifulSoup(target_response.content, 'html.parser')
            
            # 페이지 제목 확인
            title = soup.find('title')
            if title:
                print(f"   📋 페이지 제목: {title.text.strip()}")
            
            # 에러 메시지 검색
            error_divs = soup.find_all(['div', 'p', 'span'], class_=lambda x: x and ('error' in x.lower() or 'alert' in x.lower()))
            if error_divs:
                print("   ❌ 발견된 에러 메시지:")
                for error in error_divs[:3]:  # 최대 3개까지만
                    print(f"      - {error.text.strip()}")
            
            # JavaScript 에러 검색
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'error' in script.string.lower():
                    print(f"   ⚠️ JavaScript 에러 가능성 발견")
                    break
            
            # 폼 요소 확인
            forms = soup.find_all('form')
            print(f"   📝 폼 개수: {len(forms)}")
            
            # 테이블 확인 (사용자 관리 페이지이므로)
            tables = soup.find_all('table')
            print(f"   📊 테이블 개수: {len(tables)}")
            
            # 응답 텍스트의 일부 출력
            response_preview = target_response.text[:1000]
            if '500' in response_preview or 'Internal Server Error' in response_preview:
                print("   ❌ 500 Internal Server Error 감지됨")
                print("   📄 응답 내용 미리보기:")
                print(response_preview)
            elif '404' in response_preview or 'Not Found' in response_preview:
                print("   ❌ 404 Not Found 오류 감지됨")
            elif 'exception' in response_preview.lower() or 'traceback' in response_preview.lower():
                print("   ❌ Python 예외/트레이스백 감지됨")
                # 예외 내용 추출
                lines = response_preview.split('\n')
                for i, line in enumerate(lines):
                    if 'exception' in line.lower() or 'error' in line.lower():
                        print(f"   📋 오류 라인: {line.strip()}")
                        if i + 1 < len(lines):
                            print(f"   📋 다음 라인: {lines[i+1].strip()}")
                        break
            else:
                print("   ✅ 페이지가 정상적으로 로드됨")
                
        elif target_response.status_code == 404:
            print("   ❌ 404 Not Found: 페이지가 존재하지 않음")
        elif target_response.status_code == 500:
            print("   ❌ 500 Internal Server Error: 서버 내부 오류")
            print("   📄 오류 내용:")
            print(target_response.text[:500])
        elif target_response.status_code == 403:
            print("   ❌ 403 Forbidden: 접근 권한 없음")
        elif target_response.status_code == 302:
            redirect_location = target_response.headers.get('Location', '')
            print(f"   🔄 302 Redirect: {redirect_location}")
        else:
            print(f"   ❓ 예상치 못한 상태 코드: {target_response.status_code}")
        
        # 5단계: 서버 로그 확인을 위한 정보 수집
        print("📊 5단계: 디버깅 정보 수집")
        cookies = dict(session.cookies)
        print(f"   🍪 세션 쿠키 수: {len(cookies)}")
        
        if 'sessionid' in cookies:
            print(f"   ✅ Django 세션 ID: {cookies['sessionid'][:20]}...")
        if 'csrftoken' in cookies:
            print(f"   ✅ CSRF 토큰: {cookies['csrftoken'][:20]}...")
            
        return target_response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ 테스트 중 오류 발생: {e}")
        return False

def main():
    """메인 테스트 실행"""
    
    success = test_manage_sub_accounts_page()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 페이지 접근 성공 - 세부 오류 분석 필요")
    else:
        print("❌ 페이지 접근 실패 - 서버 로그 확인 필요")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()