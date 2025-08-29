#!/usr/bin/env python3
"""
메인아이디 방문차량 등록 및 대시보드 표시 종합 진단
Comprehensive diagnosis of main account visitor vehicle registration and dashboard display
"""

import asyncio
import json
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def comprehensive_visitor_vehicle_test():
    """메인아이디 방문차량 등록 및 표시 종합 테스트"""
    
    print("=" * 90)
    print("🔍 메인아이디 방문차량 등록 및 대시보드 표시 종합 진단")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # 네트워크 요청 모니터링
            requests = []
            responses = []
            
            def on_request(request):
                if 'visitor' in request.url.lower() or 'api' in request.url.lower():
                    requests.append({
                        'method': request.method,
                        'url': request.url,
                        'post_data': request.post_data if request.method == 'POST' else None
                    })
            
            def on_response(response):
                if 'visitor' in response.url.lower() or 'api' in response.url.lower():
                    responses.append({
                        'status': response.status,
                        'url': response.url
                    })
            
            page.on('request', on_request)
            page.on('response', on_response)
            
            # 1단계: 메인아이디 로그인
            print("\n🔐 1단계: 메인아이디 로그인 테스트")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            # 로그인 폼 확인
            username_field = page.locator('input[name="username"]')
            password_field = page.locator('input[name="password"]')
            submit_button = page.locator('button[type="submit"]')
            
            if await username_field.count() > 0:
                await username_field.fill("newtest1754832743")
                await password_field.fill("admin123")
                await submit_button.click()
                await page.wait_for_load_state('networkidle')
                
                current_url = page.url
                if "dashboard" in current_url:
                    print(f"   ✅ 로그인 성공: {current_url}")
                else:
                    print(f"   ❌ 로그인 실패: {current_url}")
                    return False
            else:
                print("   ❌ 로그인 폼을 찾을 수 없습니다")
                return False
            
            # 2단계: 대시보드 현재 상태 확인
            print("\n📊 2단계: 대시보드 현재 방문차량 상태 확인")
            
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 버튼 찾기
            visitor_buttons = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 방문차량 관련 버튼/요소: {len(visitor_buttons)}개")
            
            visitor_count_text = ""
            for i, button in enumerate(visitor_buttons):
                try:
                    text = await button.inner_text()
                    print(f"      {i+1}. '{text.strip()}'")
                    if "방문차량" in text:
                        visitor_count_text = text.strip()
                except:
                    continue
            
            # 3단계: 새로운 방문차량 등록
            print("\n🚗 3단계: 새로운 방문차량 등록")
            
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            # 현재 시간 기준으로 유니크한 차량번호 생성
            test_vehicle = f"진단{int(time.time()) % 10000}"
            today = date.today().strftime('%Y-%m-%d')
            
            print(f"   🔖 등록할 차량번호: {test_vehicle}")
            
            # 폼 입력
            try:
                await page.fill('input[name="visitor_name"]', "진단테스트방문자")
                await page.fill('input[name="visitor_phone"]', "010-1234-5678")
                await page.fill('input[name="vehicle_number"]', test_vehicle)
                await page.fill('input[name="visit_date"]', today)
                await page.fill('input[name="visit_time"]', "18:00")
                await page.fill('input[name="purpose"]', "시스템 진단 테스트")
                
                print("   ✅ 폼 입력 완료")
                
                # 폼 제출
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # 성공 메시지 확인
                page_content = await page.content()
                if "성공적으로 등록" in page_content:
                    print("   ✅ 방문차량 등록 성공")
                else:
                    print("   ⚠️ 등록 성공 메시지 미확인")
                
            except Exception as e:
                print(f"   ❌ 등록 중 오류: {e}")
                return False
            
            # 4단계: 대시보드로 돌아가서 확인
            print("\n🔄 4단계: 대시보드에서 등록된 방문차량 확인")
            
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 카운트 다시 확인
            updated_visitor_buttons = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 업데이트된 방문차량 요소: {len(updated_visitor_buttons)}개")
            
            visitor_count_updated = False
            for button in updated_visitor_buttons:
                try:
                    text = await button.inner_text()
                    print(f"      - '{text.strip()}'")
                    if "방문차량" in text and "0" not in text:
                        visitor_count_updated = True
                        print(f"   ✅ 방문차량 카운트가 0이 아님!")
                except:
                    continue
            
            # 방문차량 버튼 클릭
            print("\n🔍 5단계: 방문차량 버튼 클릭하여 상세 확인")
            
            visitor_button_clicked = False
            visitor_links = await page.locator('a:has-text("방문차량"), button:has-text("방문차량")').all()
            
            for link in visitor_links:
                try:
                    text = await link.inner_text()
                    if "방문차량" in text:
                        print(f"   🖱️ 방문차량 버튼 클릭: '{text}'")
                        await link.click()
                        await page.wait_for_load_state('networkidle')
                        await asyncio.sleep(3)
                        
                        visitor_button_clicked = True
                        break
                except Exception as e:
                    print(f"   ⚠️ 버튼 클릭 실패: {e}")
                    continue
            
            if visitor_button_clicked:
                # 클릭 후 페이지 상태 확인
                current_url = page.url
                current_content = await page.content()
                
                print(f"   📍 클릭 후 URL: {current_url}")
                
                if test_vehicle in current_content:
                    print(f"   ✅ 등록된 차량({test_vehicle})이 표시됨!")
                else:
                    print(f"   ❌ 등록된 차량({test_vehicle})이 표시되지 않음")
                    
                    # 디버깅: 페이지 상태 분석
                    if "등록된 방문차량이 없습니다" in current_content:
                        print("   📋 '등록된 방문차량이 없습니다' 메시지 표시됨")
                    elif "방문차량등록 버튼을 눌러" in current_content:
                        print("   📋 '방문차량등록 버튼을 눌러 새로운 방문차량을 등록하세요' 메시지 표시됨")
                    else:
                        print("   📋 알 수 없는 상태")
            
            # 6단계: API 직접 확인
            print("\n🛠️ 6단계: 방문차량 API 직접 확인")
            
            try:
                # 방문차량 API 직접 호출
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                
                print(f"   📡 API 응답 상태: {api_response.status}")
                
                if api_response.status == 200:
                    try:
                        api_data = await api_response.json()
                        print(f"   📊 API 응답: {len(api_data.get('vehicles', []))}개 방문차량")
                        
                        # 등록한 차량이 API 응답에 있는지 확인
                        vehicles = api_data.get('vehicles', [])
                        found_in_api = False
                        for vehicle in vehicles:
                            if test_vehicle in str(vehicle):
                                print(f"   ✅ API에서 등록한 차량 확인!")
                                found_in_api = True
                                break
                        
                        if not found_in_api and vehicles:
                            print(f"   ❌ API에서 등록한 차량 미확인")
                            print(f"   📋 API 응답 예시: {vehicles[:1] if vehicles else 'empty'}")
                        elif not vehicles:
                            print(f"   ❌ API 응답이 비어있음")
                            
                    except json.JSONDecodeError:
                        api_text = await api_response.text()
                        print(f"   ❌ API JSON 파싱 실패: {api_text[:200]}...")
                        
                elif api_response.status == 403:
                    print("   ❌ API 접근 권한 없음 (403)")
                else:
                    print(f"   ❌ API 응답 오류: {api_response.status}")
                    
            except Exception as e:
                print(f"   ❌ API 호출 오류: {e}")
            
            # 7단계: 네트워크 요청 분석
            print("\n🌐 7단계: 네트워크 요청 분석")
            
            print(f"   📡 방문차량 관련 요청: {len(requests)}개")
            for req in requests:
                print(f"      {req['method']} {req['url']}")
                if req['post_data']:
                    print(f"         데이터: {req['post_data'][:100]}...")
            
            print(f"   📡 방문차량 관련 응답: {len(responses)}개")
            for resp in responses:
                print(f"      {resp['status']} {resp['url']}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/comprehensive_diagnosis_{datetime.now().strftime('%H%M%S')}.png")
            
            # 결과 종합
            results = {
                'login_success': "dashboard" in page.url,
                'registration_success': "성공적으로 등록" in (await page.content()),
                'visitor_count_updated': visitor_count_updated,
                'visitor_button_clicked': visitor_button_clicked,
                'api_accessible': api_response.status == 200 if 'api_response' in locals() else False,
                'test_vehicle': test_vehicle
            }
            
            return results
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/diagnosis_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창을 확인하고 Enter를 누르면 종료됩니다...")
            await asyncio.sleep(10)  # 10초 대기
            await browser.close()

async def main():
    """메인 함수"""
    result = await comprehensive_visitor_vehicle_test()
    
    print("\n" + "=" * 90)
    print("📊 종합 진단 결과")
    print("=" * 90)
    
    if result and isinstance(result, dict):
        print("📋 상세 분석:")
        print(f"   🔐 로그인: {'성공' if result['login_success'] else '실패'}")
        print(f"   📝 방문차량 등록: {'성공' if result['registration_success'] else '실패'}")
        print(f"   📊 대시보드 카운트 업데이트: {'YES' if result['visitor_count_updated'] else 'NO'}")
        print(f"   🖱️ 방문차량 버튼 클릭: {'성공' if result['visitor_button_clicked'] else '실패'}")
        print(f"   🛠️ API 접근: {'가능' if result['api_accessible'] else '불가능'}")
        print(f"   🚗 테스트 차량: {result['test_vehicle']}")
        
        if result['registration_success'] and not result['visitor_count_updated']:
            print(f"\n🎯 문제 식별:")
            print(f"   ❌ 방문차량 등록은 성공하지만 대시보드에 반영되지 않음")
            print(f"   📝 해결 필요: API 또는 대시보드 로직 수정")
            
    else:
        print("❌ 진단 실행 중 오류 발생")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())