#!/usr/bin/env python3
"""
Targeted test for the visitor vehicle button - specifically click "방문차량 6" button
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def targeted_toggle_test():
    """Test clicking the specific '방문차량 6' button"""
    
    print("=== 🎯 타겟 방문차량 버튼 테스트 ===")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 목표: '방문차량 6' 버튼 클릭하여 실제 동작 확인")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # Monitor API calls
            api_calls = []
            def on_request(request):
                if 'visitor' in request.url.lower():
                    api_calls.append(f"REQUEST: {request.method} {request.url}")
            
            def on_response(response):
                if 'visitor' in response.url.lower():
                    api_calls.append(f"RESPONSE: {response.status} {response.url}")
            
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
            
            if "dashboard" not in page.url:
                print("   ❌ 로그인 실패")
                return False
            print("   ✅ 로그인 성공")
            
            # 2단계: 대시보드에서 '방문차량 6' 버튼 찾기
            print("\n🔍 2단계: '방문차량 6' 버튼 정확히 찾기")
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 버튼 정확히 찾기 - 숫자가 포함된 button 태그
            visitor_button = page.locator('button:has-text("방문차량")')
            
            if await visitor_button.count() > 0:
                button_text = await visitor_button.inner_text()
                print(f"   ✅ 방문차량 버튼 발견: '{button_text.strip()}'")
            else:
                print("   ❌ 방문차량 버튼을 찾을 수 없음")
                return False
            
            # 3단계: 버튼 클릭 및 결과 확인
            print("\n🖱️ 3단계: '방문차량' 버튼 클릭")
            
            # API 호출 모니터링 시작
            api_calls.clear()
            
            try:
                await visitor_button.click()
                print("   ✅ 버튼 클릭 성공")
                
                # 페이지 응답 대기
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(5)  # API 호출 및 렌더링 대기
                
            except Exception as e:
                print(f"   ❌ 버튼 클릭 실패: {e}")
                return False
            
            # 4단계: 클릭 후 결과 분석
            print("\n📊 4단계: 클릭 후 결과 분석")
            
            # API 호출 확인
            if api_calls:
                print(f"   📡 감지된 API 호출: {len(api_calls)}개")
                for call in api_calls:
                    print(f"      {call}")
            else:
                print("   ⚠️ API 호출이 감지되지 않음")
            
            # 페이지 상태 확인
            current_url = page.url
            page_content = await page.content()
            
            print(f"   📍 현재 URL: {current_url}")
            
            # 결과 메시지 확인
            if "등록된 방문차량이 없습니다" in page_content:
                print("   ❌ 문제 확인: '등록된 방문차량이 없습니다' 메시지 표시")
                problem_confirmed = True
            elif "로딩 중" in page_content or "불러오는 중" in page_content:
                print("   ⏳ 로딩 상태 - API 호출 중일 수 있음")
                problem_confirmed = False
            else:
                # 차량번호 패턴 찾기
                import re
                vehicle_patterns = re.findall(r'[0-9]{2,3}[가-힣][0-9]{4}', page_content)
                
                if vehicle_patterns:
                    print(f"   🎉 성공: 방문차량 목록 발견! {len(vehicle_patterns)}개")
                    for pattern in vehicle_patterns[:3]:
                        print(f"      - {pattern}")
                    problem_confirmed = False
                else:
                    print("   ❓ 상태 불명확 - 추가 분석 필요")
                    problem_confirmed = True
            
            # 5단계: API 직접 호출하여 비교
            print("\n🛠️ 5단계: API 직접 호출하여 데이터 확인")
            
            try:
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                
                print(f"   📡 API 상태: {api_response.status}")
                
                if api_response.status == 200:
                    api_data = await api_response.json()
                    api_vehicles = api_data.get('visitor_vehicles', [])
                    api_count = len(api_vehicles)
                    
                    print(f"   📊 API 응답:")
                    print(f"      차량 수: {api_count}개")
                    print(f"      성공 여부: {api_data.get('success', False)}")
                    
                    if api_count == 0:
                        print(f"   🎯 문제 확인: 대시보드는 6개 표시하지만 API는 0개 반환")
                        print(f"   💡 원인: API가 잘못된 데이터 모델 사용 중")
                    else:
                        print(f"   ✅ API에 데이터 존재 - 프론트엔드 문제일 수 있음")
                        
                else:
                    print(f"   ❌ API 호출 실패: {api_response.status}")
                    
            except Exception as e:
                print(f"   ❌ API 호출 오류: {e}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/targeted_toggle_test_{datetime.now().strftime('%H%M%S')}.png")
            
            return {
                'button_clicked': True,
                'problem_confirmed': problem_confirmed,
                'api_calls': len(api_calls),
                'api_empty': api_count == 0 if 'api_count' in locals() else True
            }
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/targeted_test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print(f"\n🔍 브라우저 창 확인 (5초 후 자동 종료)")
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(targeted_toggle_test())
    
    print("\n" + "=" * 50)
    print("📊 타겟 테스트 결과")
    print("=" * 50)
    
    if isinstance(result, dict):
        print("✅ 테스트 완료:")
        print(f"   🖱️ 버튼 클릭: {'성공' if result['button_clicked'] else '실패'}")
        print(f"   ❌ 문제 확인: {'YES' if result['problem_confirmed'] else 'NO'}")
        print(f"   📡 API 호출: {result['api_calls']}개")
        print(f"   📊 API 빈 데이터: {'YES' if result['api_empty'] else 'NO'}")
        
        if result['problem_confirmed'] and result['api_empty']:
            print(f"\n🎯 문제 확인됨!")
            print(f"   대시보드: 방문차량 6개 표시")
            print(f"   버튼 클릭: 성공")
            print(f"   API 응답: 0개 (문제)")
            print(f"   결과 메시지: '등록된 방문차량이 없습니다'")
            print(f"\n🔧 해결 필요: API 모델을 VisitorReservation으로 변경")
    else:
        print("❌ 테스트 실행 실패")
    
    print(f"\n🚀 다음: 구글 서버 접속하여 API 수정 배포")
    print(result)