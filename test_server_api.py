#!/usr/bin/env python3
"""
서버 API 직접 테스트 스크립트
Android 앱과 동일한 방식으로 서버 API 호출하여 실제 응답 확인
"""

import requests
import json
import time
from datetime import datetime

def test_login_and_get_token():
    """로그인하여 인증 토큰 획득"""
    login_url = "https://aptgo.org/api/login/"
    login_data = {
        "username": "newtest1754832743",
        "password": "admin123"
    }
    
    print(f"🔐 로그인 시도: {login_url}")
    print(f"   - 사용자명: {login_data['username']}")
    
    try:
        response = requests.post(login_url, json=login_data, timeout=30)
        print(f"   - 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - 로그인 성공: {data.get('success', False)}")
            
            # 토큰 확인 (여러 가능한 필드명 체크)
            token = data.get('token') or data.get('accessToken') or data.get('access_token')
            if token:
                print(f"   - 토큰 획득: {token[:20]}...")
                return token
            else:
                print(f"   - 토큰 없음. 응답 데이터: {data}")
                return None
        else:
            print(f"   - 로그인 실패: {response.text}")
            return None
            
    except Exception as e:
        print(f"   - 로그인 오류: {e}")
        return None

def test_comprehensive_api(token):
    """ComprehensiveVehicleData API 테스트"""
    api_url = "https://aptgo.org/api/comprehensive/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 API 호출: {api_url}")
    print(f"   - Authorization: Bearer {token[:20]}...")
    
    try:
        start_time = time.time()
        response = requests.get(api_url, headers=headers, timeout=60)  # 60초 타임아웃
        end_time = time.time()
        
        print(f"   - 응답 코드: {response.status_code}")
        print(f"   - 응답 시간: {end_time - start_time:.2f}초")
        print(f"   - 응답 크기: {len(response.content):,} bytes ({len(response.content)/1024:.1f} KB)")
        
        if response.status_code == 200:
            data = response.json()
            
            # 응답 구조 분석
            print(f"\n📊 응답 데이터 분석:")
            print(f"   - success: {data.get('success')}")
            print(f"   - message: {data.get('message')}")
            
            # 차량 데이터
            vehicles = data.get('vehicles', [])
            print(f"   - 차량 데이터 수: {len(vehicles)}개")
            
            if vehicles:
                print(f"   - 첫 번째 차량 샘플:")
                first_vehicle = vehicles[0]
                for key, value in first_vehicle.items():
                    print(f"     * {key}: {value}")
            
            # 서브 계정 데이터
            sub_accounts = data.get('subAccounts', [])
            print(f"   - 서브 계정 수: {len(sub_accounts)}개")
            
            # 주민 데이터
            residents = data.get('residents', [])
            print(f"   - 주민 데이터 수: {len(residents)}개")
            
            # 방문자 차량
            visitor_vehicles = data.get('visitorVehicles', [])
            print(f"   - 방문자 차량 수: {len(visitor_vehicles)}개")
            
            return data
            
        else:
            print(f"   - API 호출 실패")
            print(f"   - 응답 헤더: {dict(response.headers)}")
            print(f"   - 응답 내용: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"   - 타임아웃 오류: 60초 내에 응답 없음")
        return None
    except Exception as e:
        print(f"   - API 호출 오류: {e}")
        return None

def analyze_data_discrepancy(api_data):
    """데이터 불일치 분석"""
    if not api_data:
        return
        
    print(f"\n🔍 데이터 불일치 분석:")
    
    vehicles = api_data.get('vehicles', [])
    sub_accounts = api_data.get('subAccounts', [])
    
    print(f"   - 서버 응답 차량 수: {len(vehicles)}개")
    print(f"   - 서버 응답 서브 계정 수: {len(sub_accounts)}개")
    print(f"   - 예상 데이터 수: 299개")
    
    if len(vehicles) < 299:
        print(f"   ⚠️ 차량 데이터 부족: {299 - len(vehicles)}개 누락")
    
    # 데이터 품질 확인
    valid_vehicles = 0
    for vehicle in vehicles[:10]:  # 처음 10개만 체크
        if vehicle.get('plateNumber') and vehicle.get('ownerName'):
            valid_vehicles += 1
    
    print(f"   - 유효 차량 데이터 비율: {valid_vehicles}/10 (샘플)")
    
    # 차량 타입별 분석
    vehicle_types = {}
    for vehicle in vehicles:
        vtype = vehicle.get('vehicleType', 'unknown')
        vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
    
    print(f"   - 차량 타입별 분포:")
    for vtype, count in vehicle_types.items():
        print(f"     * {vtype}: {count}개")

def save_response_to_file(api_data, filename="server_response.json"):
    """서버 응답을 파일로 저장"""
    if api_data:
        with open(f"/Users/dragonship/파이썬/aptgoapp/{filename}", 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 서버 응답 저장됨: {filename}")

def main():
    print("=" * 60)
    print("🧪 서버 API 직접 테스트")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1단계: 로그인
    token = test_login_and_get_token()
    if not token:
        print("❌ 로그인 실패. 테스트 중단.")
        return
    
    # 2단계: API 호출
    api_data = test_comprehensive_api(token)
    
    # 3단계: 데이터 분석
    analyze_data_discrepancy(api_data)
    
    # 4단계: 응답 저장
    save_response_to_file(api_data)
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    print("=" * 60)
    
    return api_data

if __name__ == "__main__":
    result = main()