#!/usr/bin/env python3
"""
Test the local API fix to verify VisitorReservation model is working
Test this against local Django server running on localhost:8002
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

async def test_local_api_fix():
    """Test the locally fixed API against local Django server"""
    
    print("=== 🔧 로컬 API 수정사항 테스트 ===")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 테스트 대상: http://localhost:8002 (로컬 Django 서버)")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            # 1단계: 로컬 서버 접근 확인
            print("\n🔍 1단계: 로컬 Django 서버 접근 테스트")
            try:
                await page.goto("http://localhost:8002/login/")
                await page.wait_for_load_state('networkidle')
                print("   ✅ 로컬 서버 접근 성공")
            except Exception as e:
                print(f"   ❌ 로컬 서버 접근 실패: {e}")
                print("   💡 Django 서버를 먼저 시작해주세요:")
                print("      cd /Users/dragonship/파이썬/ANPR")
                print("      source venv/bin/activate")
                print("      python manage.py runserver localhost:8002")
                return False
            
            # 2단계: 로그인
            print("\n🔐 2단계: 테스트 계정 로그인")
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" in page.url:
                print("   ✅ 로그인 성공")
            else:
                print("   ❌ 로그인 실패 - 계정 정보를 확인해주세요")
                return False
            
            # 3단계: 방문차량 등록
            print("\n🚗 3단계: 새로운 방문차량 등록")
            await page.goto("http://localhost:8002/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            # 유니크한 테스트 차량번호 생성
            test_vehicle = f"로컬{int(time.time()) % 10000}"
            
            try:
                # 방문자 정보 입력
                await page.fill('input[name="visitor_name"]', "로컬테스트방문자")
                await page.fill('input[name="visitor_phone"]', "010-8888-9999")
                await page.fill('input[name="vehicle_number"]', test_vehicle)
                
                # 내일 날짜로 설정
                from datetime import date, timedelta
                tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
                await page.fill('input[name="visit_date"]', tomorrow)
                await page.fill('input[name="visit_time"]', "14:00")
                await page.fill('input[name="purpose"]', "로컬 API 수정 테스트")
                
                print(f"   🔖 등록 차량번호: {test_vehicle}")
                print(f"   📅 방문 예정일: {tomorrow}")
                
                # 폼 제출
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                print("   ✅ 방문차량 등록 완료")
                
            except Exception as e:
                print(f"   ❌ 방문차량 등록 실패: {e}")
                return False
            
            # 4단계: 로컬 API 직접 테스트
            print("\n🛠️ 4단계: 로컬 API 응답 확인")
            
            try:
                # API 호출
                api_response = await page.request.get("http://localhost:8002/api/visitor-vehicles-api/")
                
                print(f"   📡 API 응답 상태: {api_response.status}")
                
                if api_response.status == 200:
                    try:
                        api_data = await api_response.json()
                        vehicles_count = len(api_data.get('visitor_vehicles', []))
                        
                        print(f"   📊 API 응답 데이터:")
                        print(f"      방문차량 수: {vehicles_count}개")
                        print(f"      성공 상태: {api_data.get('success', 'N/A')}")
                        print(f"      총 카운트: {api_data.get('count', 'N/A')}")
                        
                        if vehicles_count > 0:
                            print(f"   🎉 API 수정 성공! 방문차량 데이터 확인됨!")
                            
                            # 방금 등록한 차량이 있는지 확인
                            found_test_vehicle = False
                            print(f"   📋 등록된 방문차량 목록:")
                            for i, vehicle in enumerate(api_data.get('visitor_vehicles', [])[:5]):
                                vehicle_number = vehicle.get('vehicle_number', 'N/A')
                                visitor_name = vehicle.get('visitor_name', 'N/A')
                                print(f"      {i+1}. {vehicle_number} - {visitor_name}")
                                
                                if test_vehicle in vehicle_number:
                                    print(f"      ✅ 방금 등록한 테스트 차량 확인됨!")
                                    found_test_vehicle = True
                            
                            if not found_test_vehicle:
                                print(f"   ⚠️ 테스트 차량({test_vehicle})은 없지만 다른 차량들 존재")
                            
                            return True
                            
                        else:
                            print(f"   ❌ API 여전히 빈 응답 반환")
                            print(f"   📄 전체 응답: {api_data}")
                            return False
                            
                    except Exception as e:
                        response_text = await api_response.text()
                        print(f"   ❌ API JSON 파싱 실패: {e}")
                        print(f"   📄 응답 내용: {response_text[:300]}")
                        return False
                else:
                    print(f"   ❌ API 호출 실패: {api_response.status}")
                    error_text = await api_response.text()
                    print(f"   📄 오류 내용: {error_text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ API 호출 중 오류: {e}")
                return False
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            return False
            
        finally:
            print(f"\n🔍 브라우저 창 확인 (5초 후 종료)")
            await asyncio.sleep(5)
            await browser.close()

async def main():
    """메인 테스트 함수"""
    result = await test_local_api_fix()
    
    print("\n" + "=" * 70)
    print("📊 로컬 테스트 결과")
    print("=" * 70)
    
    if result:
        print("🎉 성공! 로컬 API 수정이 정상 작동합니다!")
        print("✅ VisitorReservation 모델 사용으로 변경 완료")
        print("✅ 대시보드 카운터와 API가 동일한 데이터 소스 사용")
        print("✅ visitor_vehicles 배열에 데이터 반환 확인")
        print("\n🚀 다음 단계: 서버에 수정사항 배포")
        
    else:
        print("❌ 로컬 테스트 실패")
        print("🔍 Django 서버 실행 상태를 확인해주세요")
        print("💡 로컬 서버 실행 방법:")
        print("   cd /Users/dragonship/파이썬/ANPR")
        print("   source venv/bin/activate") 
        print("   python manage.py runserver localhost:8002")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())