#!/usr/bin/env python3
"""
메인아이디 대시보드 방문차량 표시 문제 진단
방문차량 등록 후 대시보드에서 표시되지 않는 문제 해결
"""

import asyncio
import json
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def test_dashboard_visitor_display():
    """대시보드 방문차량 표시 문제 진단"""
    
    print("=" * 80)
    print("🔍 메인아이디 대시보드 방문차량 표시 문제 진단")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        
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
            
            # 2단계: 대시보드에서 현재 방문차량 상태 확인
            print("\n📊 2단계: 대시보드 현재 방문차량 상태 확인")
            
            # 방문차량 버튼/링크 찾기
            visitor_buttons = await page.locator('*:has-text("방문차량"), a[href*="visitor"], button:has-text("방문")').all()
            print(f"   📋 방문차량 관련 요소: {len(visitor_buttons)}개")
            
            for i, button in enumerate(visitor_buttons[:5]):
                try:
                    text = await button.inner_text()
                    tag_name = await button.evaluate('el => el.tagName')
                    href = await button.get_attribute('href') if tag_name == 'A' else 'N/A'
                    print(f"      {i+1}. [{tag_name}] '{text.strip()}' → {href}")
                except:
                    continue
            
            # 현재 대시보드 HTML 내용 확인
            dashboard_content = await page.content()
            
            # 방문차량 관련 텍스트 검색
            visitor_keywords = ["방문차량", "visitor", "방문자", "등록"]
            found_keywords = []
            for keyword in visitor_keywords:
                if keyword in dashboard_content:
                    found_keywords.append(keyword)
            
            print(f"   🔍 발견된 방문차량 관련 키워드: {', '.join(found_keywords)}")
            
            # 3단계: 새 방문차량 등록
            print("\n🚗 3단계: 새 방문차량 등록 테스트")
            
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"대시보드{int(time.time()) % 10000}"
            
            # 폼 입력
            await page.fill('input[name="visitor_name"]', "대시보드테스트방문자")
            await page.fill('input[name="visitor_phone"]', "010-8888-9999")
            await page.fill('input[name="vehicle_number"]', test_vehicle)
            await page.fill('input[name="visit_date"]', today)
            await page.fill('input[name="visit_time"]', "18:00")
            await page.fill('input[name="purpose"]', "대시보드 표시 테스트")
            
            print(f"   ✅ 등록 정보 입력 완료: {test_vehicle}")
            
            # 폼 제출
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # 등록 성공 확인
            registration_content = await page.content()
            registration_success = "성공적으로 등록" in registration_content
            print(f"   {'✅' if registration_success else '❌'} 등록 {'성공' if registration_success else '실패'}")
            
            # 4단계: 대시보드로 돌아가서 즉시 확인
            print("\n🔄 4단계: 대시보드 새로고침 후 방문차량 확인")
            
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 로딩 대기
            
            # 새로운 대시보드 내용 확인
            updated_dashboard_content = await page.content()
            
            # 등록한 차량번호가 표시되는지 확인
            vehicle_displayed = test_vehicle in updated_dashboard_content
            print(f"   {'✅' if vehicle_displayed else '❌'} 등록한 차량번호({test_vehicle}) 대시보드 표시: {'YES' if vehicle_displayed else 'NO'}")
            
            # 방문차량 버튼 다시 확인
            updated_visitor_buttons = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 업데이트된 방문차량 요소: {len(updated_visitor_buttons)}개")
            
            for i, button in enumerate(updated_visitor_buttons[:3]):
                try:
                    text = await button.inner_text()
                    print(f"      {i+1}. '{text.strip()}'")
                    # 방문차량 0이 아닌 숫자가 나오는지 확인
                    if "방문차량" in text and "0" not in text:
                        print(f"         ✅ 방문차량 카운트가 업데이트됨!")
                except:
                    continue
            
            # 5단계: 방문차량 버튼 클릭해서 상세 확인
            print("\n🔍 5단계: 방문차량 버튼 클릭하여 상세 페이지 확인")
            
            # 방문차량 관련 링크 클릭
            visitor_link_found = False
            visitor_links = await page.locator('a:has-text("방문차량"), a[href*="visitor"]').all()
            
            for link in visitor_links:
                try:
                    text = await link.inner_text()
                    href = await link.get_attribute('href')
                    
                    if "방문차량" in text or "visitor" in href:
                        print(f"   🔗 방문차량 링크 클릭: '{text}' → {href}")
                        
                        # 링크 클릭
                        await link.click()
                        await page.wait_for_load_state('networkidle')
                        
                        # 이동된 페이지 확인
                        current_url = page.url
                        current_title = await page.title()
                        current_content = await page.content()
                        
                        print(f"   📍 이동된 페이지: {current_url}")
                        print(f"   📋 페이지 제목: {current_title}")
                        
                        # 등록한 차량이 목록에 있는지 확인
                        if test_vehicle in current_content:
                            print(f"   ✅ 방문차량 상세 페이지에서 등록한 차량 확인!")
                        else:
                            print(f"   ❌ 방문차량 상세 페이지에서 등록한 차량 미확인")
                            
                            # 페이지 내용 분석
                            if "방문차량이 없습니다" in current_content:
                                print(f"   📋 '방문차량이 없습니다' 메시지 표시됨")
                            elif "로딩" in current_content or "Loading" in current_content:
                                print(f"   📋 페이지가 아직 로딩 중인 것으로 보임")
                            else:
                                print(f"   📋 알 수 없는 상태 - 수동 확인 필요")
                        
                        visitor_link_found = True
                        break
                        
                except Exception as e:
                    print(f"   ⚠️ 링크 클릭 오류: {e}")
                    continue
            
            if not visitor_link_found:
                print(f"   ❌ 클릭 가능한 방문차량 링크를 찾을 수 없음")
            
            # 6단계: 데이터베이스 상태 직접 확인 (API 호출)
            print("\n🗄️ 6단계: 데이터베이스 상태 API로 확인")
            
            try:
                # 방문차량 API 호출
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                
                if api_response.status == 200:
                    api_data = await api_response.json()
                    print(f"   📊 API 응답: 총 {len(api_data)}개 방문차량")
                    
                    # 최근 등록한 차량 찾기
                    found_in_api = False
                    for vehicle in api_data:
                        vehicle_str = str(vehicle)
                        if test_vehicle in vehicle_str:
                            print(f"   ✅ API에서 등록한 차량 확인: {test_vehicle}")
                            found_in_api = True
                            break
                    
                    if not found_in_api:
                        print(f"   ❌ API에서 등록한 차량({test_vehicle}) 미확인")
                        print(f"   📋 API 데이터 예시: {api_data[:2] if api_data else 'empty'}")
                    
                else:
                    print(f"   ❌ API 응답 오류: {api_response.status}")
                    
            except Exception as e:
                print(f"   ⚠️ API 호출 오류: {e}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/dashboard_test_{datetime.now().strftime('%H%M%S')}.png")
            
            # 결과 종합
            results = {
                'registration_success': registration_success,
                'vehicle_displayed_dashboard': vehicle_displayed,
                'visitor_link_found': visitor_link_found,
                'test_vehicle': test_vehicle
            }
            
            return results
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/dashboard_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창을 수동으로 확인하고 Enter를 누르면 종료됩니다...")
            await asyncio.sleep(5)  # 자동 대기
            await browser.close()

async def main():
    """메인 함수"""
    result = await test_dashboard_visitor_display()
    
    print("\n" + "=" * 80)
    print("📊 대시보드 방문차량 표시 진단 결과")
    print("=" * 80)
    
    if result and isinstance(result, dict):
        print(f"📋 상세 분석:")
        print(f"   ✅ 방문차량 등록: {'성공' if result['registration_success'] else '실패'}")
        print(f"   📊 대시보드 차량 표시: {'YES' if result['vehicle_displayed_dashboard'] else 'NO'}")
        print(f"   🔗 방문차량 링크: {'발견됨' if result['visitor_link_found'] else '미발견'}")
        print(f"   🚗 테스트 차량: {result['test_vehicle']}")
        
        if result['registration_success'] and not result['vehicle_displayed_dashboard']:
            print(f"\n🎯 문제 식별:")
            print(f"   ❌ 방문차량 등록은 성공하지만 대시보드에 표시되지 않음")
            print(f"   📝 해결 필요사항: 대시보드 템플릿 또는 뷰 로직 수정")
            
        elif result['registration_success'] and result['vehicle_displayed_dashboard']:
            print(f"\n🎉 시스템 정상:")
            print(f"   ✅ 등록도 성공하고 대시보드 표시도 정상")
            
    else:
        print("❌ 진단 실행 중 오류 발생")
        print("📝 스크린샷과 로그를 확인해주세요.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())