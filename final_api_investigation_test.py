#!/usr/bin/env python3
"""
Final comprehensive API investigation test
Test the actual API endpoints to understand data flow
"""

import asyncio
import json
import requests
from datetime import datetime
from playwright.async_api import async_playwright

async def final_api_investigation():
    """Comprehensive API investigation to understand data flow"""
    
    print("=== 🔍 최종 API 조사 및 방문차량 등록 테스트 ===")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # 네트워크 요청/응답 모니터링
            requests_log = []
            responses_log = []
            
            def on_request(request):
                if 'visitor' in request.url.lower() or 'api' in request.url.lower():
                    requests_log.append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'method': request.method,
                        'url': request.url,
                        'headers': dict(request.headers),
                        'post_data': request.post_data
                    })
            
            def on_response(response):
                if 'visitor' in response.url.lower() or 'api' in response.url.lower():
                    responses_log.append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'status': response.status,
                        'url': response.url,
                        'headers': dict(response.headers)
                    })
            
            page.on('request', on_request)
            page.on('response', on_response)
            
            # 1단계: 로그인
            print("\n🔐 1단계: 메인아이디 로그인")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" in page.url:
                print(f"   ✅ 로그인 성공: {page.url}")
            else:
                print(f"   ❌ 로그인 실패: {page.url}")
                return
            
            # 2단계: 대시보드 확인
            print("\n📊 2단계: 대시보드 방문차량 카운터 확인")
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 관련 요소들 찾기
            visitor_elements = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 방문차량 관련 요소: {len(visitor_elements)}개")
            
            dashboard_count = "알 수 없음"
            for element in visitor_elements:
                try:
                    text = await element.inner_text()
                    print(f"      - '{text.strip()}'")
                    
                    # 숫자가 포함된 방문차량 텍스트 찾기
                    if "방문차량" in text and any(char.isdigit() for char in text):
                        dashboard_count = text.strip()
                        print(f"   🎯 대시보드 카운터: '{dashboard_count}'")
                except:
                    continue
            
            # 3단계: 방문차량 API 직접 호출
            print("\n🛠️ 3단계: 방문차량 API 직접 테스트")
            
            try:
                # 쿠키 가져오기 (세션 정보)
                cookies = await page.context.cookies()
                cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                # API 요청을 위한 헤더 설정
                headers = {
                    'User-Agent': await page.evaluate('() => navigator.userAgent'),
                    'Referer': 'https://aptgo.org/main-account-dashboard/',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                print(f"   📡 API 호출: GET /api/visitor-vehicles-api/")
                
                # 브라우저 내에서 API 호출
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                
                print(f"   📊 API 응답 상태: {api_response.status}")
                
                if api_response.status == 200:
                    try:
                        api_data = await api_response.json()
                        vehicles_count = len(api_data.get('vehicles', []))
                        print(f"   📋 API 응답: {vehicles_count}개 방문차량")
                        
                        if vehicles_count > 0:
                            print(f"   ✅ API에서 방문차량 데이터 확인됨!")
                            for i, vehicle in enumerate(api_data.get('vehicles', [])[:3]):
                                print(f"      {i+1}. 차량번호: {vehicle.get('vehicle_number', 'N/A')}")
                                print(f"         방문자: {vehicle.get('visitor_name', 'N/A')}")
                                print(f"         등록자: {vehicle.get('registered_by', 'N/A')}")
                                print(f"         방문날짜: {vehicle.get('visit_date', 'N/A')}")
                        else:
                            print(f"   ❌ API 응답이 비어있음")
                            print(f"   📝 전체 API 응답: {api_data}")
                            
                    except Exception as e:
                        response_text = await api_response.text()
                        print(f"   ❌ JSON 파싱 실패: {e}")
                        print(f"   📄 응답 내용 (처음 500자): {response_text[:500]}")
                        
                else:
                    print(f"   ❌ API 오류: {api_response.status}")
                    error_text = await api_response.text()
                    print(f"   📄 오류 내용: {error_text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ API 호출 중 오류: {e}")
            
            # 4단계: 새로운 방문차량 등록 테스트
            print("\n🚗 4단계: 새로운 방문차량 등록 테스트")
            
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 유니크한 차량번호 생성
            import time
            test_vehicle = f"테스트{int(time.time()) % 10000}"
            
            try:
                # 방문자 정보 입력
                await page.fill('input[name="visitor_name"]', "API테스트방문자")
                await page.fill('input[name="visitor_phone"]', "010-9999-8888")
                await page.fill('input[name="vehicle_number"]', test_vehicle)
                
                # 오늘부터 3일 후 날짜 설정
                from datetime import date, timedelta
                future_date = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
                await page.fill('input[name="visit_date"]', future_date)
                await page.fill('input[name="visit_time"]', "15:00")
                await page.fill('input[name="purpose"]', "API 조사 테스트")
                
                print(f"   🔖 등록 차량번호: {test_vehicle}")
                print(f"   📅 방문 예정일: {future_date}")
                
                # 폼 제출
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                # 등록 결과 확인
                page_content = await page.content()
                if "성공적으로 등록" in page_content or "등록" in page_content:
                    print(f"   ✅ 방문차량 등록 성공!")
                else:
                    print(f"   ⚠️ 등록 결과 불명확")
                
                # 5단계: 등록 후 API 재확인
                print("\n🔄 5단계: 등록 후 API 재확인")
                
                api_response2 = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                print(f"   📡 재확인 API 응답 상태: {api_response2.status}")
                
                if api_response2.status == 200:
                    try:
                        api_data2 = await api_response2.json()
                        vehicles_count2 = len(api_data2.get('vehicles', []))
                        print(f"   📊 등록 후 API 응답: {vehicles_count2}개 방문차량")
                        
                        # 방금 등록한 차량이 있는지 확인
                        found_new_vehicle = False
                        for vehicle in api_data2.get('vehicles', []):
                            if test_vehicle in vehicle.get('vehicle_number', ''):
                                print(f"   🎉 새로 등록한 차량 확인됨!")
                                found_new_vehicle = True
                                break
                        
                        if not found_new_vehicle and vehicles_count2 > 0:
                            print(f"   ⚠️ 새 차량은 없지만 다른 차량들 존재")
                            for i, vehicle in enumerate(api_data2.get('vehicles', [])[:2]):
                                print(f"      {i+1}. {vehicle.get('vehicle_number', 'N/A')} - {vehicle.get('visitor_name', 'N/A')}")
                                
                    except Exception as e:
                        print(f"   ❌ 등록 후 API 파싱 실패: {e}")
                
            except Exception as e:
                print(f"   ❌ 방문차량 등록 중 오류: {e}")
            
            # 6단계: 네트워크 요청 분석
            print("\n🌐 6단계: 네트워크 요청/응답 분석")
            
            print(f"   📡 캡처된 요청: {len(requests_log)}개")
            for req in requests_log:
                print(f"      [{req['time']}] {req['method']} {req['url']}")
                if req['post_data']:
                    print(f"         데이터: {req['post_data'][:100]}...")
            
            print(f"   📡 캡처된 응답: {len(responses_log)}개")
            for resp in responses_log:
                print(f"      [{resp['time']}] {resp['status']} {resp['url']}")
            
            # 결과 요약
            print("\n" + "=" * 80)
            print("📊 조사 결과 요약")
            print("=" * 80)
            
            print(f"🏷️ 대시보드 카운터: {dashboard_count}")
            print(f"📊 API 초기 응답: {api_data.get('vehicles', []) if 'api_data' in locals() else '확인 불가'}개")
            if 'api_data2' in locals():
                print(f"📊 등록 후 API 응답: {len(api_data2.get('vehicles', []))}개")
            print(f"🚗 테스트 차량: {test_vehicle}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/final_api_investigation_{datetime.now().strftime('%H%M%S')}.png")
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/api_investigation_error_{datetime.now().strftime('%H%M%S')}.png")
            
        finally:
            print(f"\n🔍 브라우저 창 유지 (10초 후 자동 종료)")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(final_api_investigation())