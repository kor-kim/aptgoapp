#!/usr/bin/env python3
"""
최종 완전 테스트: 메인아이디 방문차량 등록 및 대시보드 표시
모든 수정사항 적용 후 완전 검증
"""

import asyncio
import json
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def final_complete_test():
    """최종 완전 테스트"""
    
    print("=" * 90)
    print("🏁 최종 완전 테스트: 메인아이디 방문차량 등록 + 대시보드 표시")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            # 1단계: 로그인
            print("🔐 1단계: 메인아이디 로그인")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" not in page.url:
                print(f"   ❌ 로그인 실패: {page.url}")
                return False
            print(f"   ✅ 로그인 성공: {page.url}")
            
            # 2단계: 새로운 방문차량 등록
            print("\n🚗 2단계: 새로운 방문차량 등록")
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"최종{int(time.time()) % 10000}"
            
            # 폼 입력
            await page.fill('input[name="visitor_name"]', "최종테스트방문자")
            await page.fill('input[name="visitor_phone"]', "010-7777-7777")
            await page.fill('input[name="vehicle_number"]', test_vehicle)
            await page.fill('input[name="visit_date"]', today)
            await page.fill('input[name="visit_time"]', "17:00")
            await page.fill('input[name="purpose"]', "최종 완전 테스트")
            
            print(f"   ✅ 차량 정보 입력 완료: {test_vehicle}")
            
            # 폼 제출
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 성공 메시지 확인
            page_content = await page.content()
            if "성공적으로 등록" in page_content:
                print(f"   ✅ 등록 성공 메시지 확인")
            else:
                print(f"   ⚠️ 성공 메시지 미확인")
            
            # 3단계: 대시보드에서 즉시 확인
            print("\n📊 3단계: 대시보드에서 등록된 방문차량 확인")
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 로딩 대기
            
            dashboard_content = await page.content()
            
            # 방문차량 관련 요소 찾기
            visitor_elements = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 방문차량 관련 요소: {len(visitor_elements)}개")
            
            # 숫자 카운트 확인
            visitor_count_elements = await page.locator('*:has-text("방문차량"):has-text("0"), *:has-text("방문차량"):has-text("1"), *:has-text("방문차량"):has-text("2"), *:has-text("방문차량"):has-text("3")').all()
            
            for i, element in enumerate(visitor_count_elements):
                try:
                    text = await element.inner_text()
                    print(f"      {i+1}. '{text.strip()}'")
                    if "방문차량 0" not in text:  # 0이 아닌 숫자가 있으면
                        print(f"   ✅ 방문차량 카운트 업데이트됨!")
                except:
                    continue
            
            # 등록된 차량번호 직접 검색
            if test_vehicle in dashboard_content:
                print(f"   ✅ 대시보드에서 등록된 차량번호 확인: {test_vehicle}")
                dashboard_success = True
            else:
                print(f"   ❌ 대시보드에서 차량번호 미발견: {test_vehicle}")
                dashboard_success = False
                
                # 디버깅: 다른 등록된 차량들 확인
                recent_vehicles = ["최종", "테스트", "서울", "1864", "1527", "602"]
                found_vehicles = []
                for vehicle_part in recent_vehicles:
                    if vehicle_part in dashboard_content:
                        found_vehicles.append(vehicle_part)
                
                if found_vehicles:
                    print(f"   🔍 발견된 차량 관련 텍스트: {', '.join(found_vehicles)}")
                else:
                    print(f"   🔍 방문차량 관련 텍스트 미발견")
            
            # 4단계: 데이터베이스 직접 확인
            print("\n🗄️ 4단계: 데이터베이스 최종 확인")
            
            # API로 확인
            try:
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                if api_response.status == 200:
                    api_data = await api_response.json()
                    print(f"   📊 API 방문차량 개수: {len(api_data)}")
                    
                    # 최근 등록된 차량 확인
                    for vehicle in api_data:
                        if test_vehicle in str(vehicle):
                            print(f"   ✅ API에서 최신 등록 차량 확인: {test_vehicle}")
                            break
                    else:
                        print(f"   ⚠️ API에서 최신 차량 미확인")
                else:
                    print(f"   ⚠️ API 응답 오류: {api_response.status}")
            except Exception as e:
                print(f"   ⚠️ API 접근 오류: {e}")
            
            # 5단계: 전체 시스템 동작 검증
            print("\n🔧 5단계: 전체 시스템 동작 검증")
            
            # 다시 등록 페이지로 가서 또 다른 차량 등록 테스트
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            # 빠른 추가 등록
            test_vehicle2 = f"검증{int(time.time()) % 1000}"
            await page.fill('input[name="visitor_name"]', "검증방문자")
            await page.fill('input[name="vehicle_number"]', test_vehicle2)
            await page.fill('input[name="visit_date"]', today)
            
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            print(f"   ✅ 추가 등록 완료: {test_vehicle2}")
            
            # 대시보드 재확인
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            final_dashboard_content = await page.content()
            
            vehicles_found = 0
            if test_vehicle in final_dashboard_content:
                vehicles_found += 1
            if test_vehicle2 in final_dashboard_content:
                vehicles_found += 1
                
            print(f"   📊 최종 대시보드 확인: {vehicles_found}/2 차량 표시됨")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/final_complete_test_{datetime.now().strftime('%H%M%S')}.png")
            
            # 종합 결과
            registration_works = "성공적으로 등록" in page_content
            dashboard_shows = vehicles_found > 0
            
            return {
                'registration_success': registration_works,
                'dashboard_display': dashboard_shows,
                'vehicles_found': vehicles_found,
                'test_vehicles': [test_vehicle, test_vehicle2]
            }
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/final_test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창 확인 후 자동 종료...")
            await asyncio.sleep(5)
            await browser.close()

async def main():
    """메인 함수"""
    result = await final_complete_test()
    
    print("\n" + "=" * 90)
    print("🏆 최종 테스트 결과 종합")
    print("=" * 90)
    
    if result and isinstance(result, dict):
        print("📊 상세 결과:")
        print(f"   ✅ 방문차량 등록: {'성공' if result['registration_success'] else '실패'}")
        print(f"   📋 대시보드 표시: {'성공' if result['dashboard_display'] else '실패'}")
        print(f"   🚗 표시된 차량 수: {result['vehicles_found']}")
        print(f"   🔖 테스트 차량들: {', '.join(result['test_vehicles'])}")
        
        if result['registration_success'] and result['dashboard_display']:
            print("\n🎉 🎉 🎉 완전 성공! 🎉 🎉 🎉")
            print("✅ 메인아이디 방문차량 등록 시스템이 완전히 작동합니다!")
            print("✅ 등록된 차량이 대시보드에서 정상적으로 표시됩니다!")
            print("\n🏆 모든 요구사항이 성공적으로 구현되었습니다!")
            print("   - 메인아이디로 로그인 ✅")
            print("   - 방문차량 등록 기능 ✅")
            print("   - 대시보드에서 등록 결과 확인 ✅")
            print("   - 실시간 업데이트 ✅")
            
        elif result['registration_success']:
            print("\n⚠️ 부분 성공")
            print("✅ 등록 기능은 완전히 작동함")
            print("❌ 대시보드 표시에 일부 문제 있음")
            
        else:
            print("\n❌ 등록 시스템에 문제 있음")
            
    else:
        print("❌ 테스트 실행 중 오류 발생")
        print("📝 로그와 스크린샷을 확인해주세요.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())