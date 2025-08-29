#!/usr/bin/env python3
"""
Comprehensive test for visitor vehicle toggle button issue
Test the exact problem: main account dashboard toggle button not showing vehicles
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

async def test_visitor_toggle_button():
    """Test the visitor vehicle toggle button functionality"""
    
    print("=== 🎯 방문차량 토글 버튼 문제 테스트 ===")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 목표: 대시보드 '방문차량' 토글 버튼 클릭 시 등록된 차량 표시")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # Enable request/response monitoring
            api_calls = []
            
            def on_response(response):
                if 'visitor' in response.url.lower():
                    api_calls.append({
                        'url': response.url,
                        'status': response.status,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
            
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
            
            # 2단계: 대시보드 분석
            print("\n📊 2단계: 대시보드 방문차량 영역 분석")
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 관련 모든 요소 찾기
            visitor_elements = await page.locator('*:has-text("방문차량")').all()
            print(f"   📋 '방문차량' 관련 요소: {len(visitor_elements)}개 발견")
            
            dashboard_count = "확인불가"
            toggle_button = None
            
            for i, element in enumerate(visitor_elements):
                try:
                    text = await element.inner_text()
                    tag_name = await element.evaluate('el => el.tagName')
                    is_clickable = await element.is_enabled()
                    
                    print(f"      {i+1}. [{tag_name}] '{text.strip()[:50]}...'")
                    print(f"         클릭 가능: {is_clickable}")
                    
                    # 카운터 찾기
                    if "방문차량" in text and any(char.isdigit() for char in text):
                        dashboard_count = ''.join(filter(str.isdigit, text))
                        print(f"         🎯 카운터 발견: {dashboard_count}개")
                    
                    # 토글 버튼 찾기 (클릭 가능한 요소)
                    if is_clickable and ("방문차량" in text and len(text.strip()) < 20):
                        toggle_button = element
                        print(f"         🖱️ 토글 버튼 후보로 선택")
                    
                except Exception as e:
                    print(f"      {i+1}. 분석 실패: {e}")
            
            print(f"   📊 대시보드 카운터: {dashboard_count}개")
            
            # 3단계: 토글 버튼 클릭 테스트
            print("\n🖱️ 3단계: 방문차량 토글 버튼 클릭 테스트")
            
            if toggle_button:
                try:
                    button_text = await toggle_button.inner_text()
                    print(f"   🎯 토글 버튼 클릭: '{button_text.strip()}'")
                    
                    # 클릭 전 API 호출 상태 확인
                    api_calls.clear()
                    
                    await toggle_button.click()
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(5)  # API 호출 및 UI 업데이트 대기
                    
                    print("   ✅ 토글 버튼 클릭 완료")
                    
                except Exception as e:
                    print(f"   ❌ 토글 버튼 클릭 실패: {e}")
                    return False
            else:
                print("   ❌ 토글 버튼을 찾을 수 없음")
                return False
            
            # 4단계: 클릭 후 상태 분석
            print("\n📋 4단계: 토글 버튼 클릭 후 상태 분석")
            
            # API 호출 확인
            if api_calls:
                print(f"   📡 API 호출 감지: {len(api_calls)}개")
                for call in api_calls:
                    print(f"      [{call['time']}] {call['status']} {call['url']}")
            else:
                print("   ⚠️ API 호출 감지 안됨")
            
            # 페이지 내용 확인
            page_content = await page.content()
            
            # 방문차량 표시 상태 확인
            if "등록된 방문차량이 없습니다" in page_content:
                print("   ❌ '등록된 방문차량이 없습니다' 메시지 표시됨")
                result = "no_vehicles_message"
            elif "방문차량 정보를 불러오는 중" in page_content:
                print("   ⏳ 로딩 중 메시지 표시")
                result = "loading"
            else:
                # 차량번호 패턴 찾기
                import re
                vehicle_patterns = re.findall(r'[0-9]{2,3}[가-힣][0-9]{4}', page_content)
                
                if vehicle_patterns:
                    print(f"   🎉 방문차량 목록 표시됨: {len(vehicle_patterns)}개")
                    for i, pattern in enumerate(vehicle_patterns[:3], 1):
                        print(f"      {i}. {pattern}")
                    result = "vehicles_displayed"
                else:
                    # 테이블 형태 확인
                    if "차량번호" in page_content and "방문자" in page_content:
                        print("   ✅ 방문차량 테이블 구조 확인됨")
                        result = "table_structure"
                    else:
                        print("   ❓ 방문차량 표시 상태 불명확")
                        result = "unclear"
            
            # 5단계: API 직접 확인
            print("\n🛠️ 5단계: 방문차량 API 직접 호출 확인")
            
            try:
                api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                print(f"   📡 API 응답 상태: {api_response.status}")
                
                if api_response.status == 200:
                    api_data = await api_response.json()
                    api_count = len(api_data.get('visitor_vehicles', []))
                    success_status = api_data.get('success', False)
                    
                    print(f"   📊 API 응답 분석:")
                    print(f"      방문차량 수: {api_count}개")
                    print(f"      성공 상태: {success_status}")
                    print(f"      전체 응답: {api_data}")
                    
                    if api_count == 0:
                        print("   🔍 문제 확인: API가 0개 차량 반환")
                    else:
                        print("   ✅ API에서 차량 데이터 확인됨")
                
            except Exception as e:
                print(f"   ❌ API 호출 오류: {e}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/visitor_toggle_test_{datetime.now().strftime('%H%M%S')}.png")
            
            # 결과 정리
            test_results = {
                'dashboard_count': dashboard_count,
                'toggle_clickable': toggle_button is not None,
                'api_calls_detected': len(api_calls) > 0,
                'display_result': result
            }
            
            return test_results
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/toggle_test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print(f"\n🔍 브라우저 창 확인 (8초 후 자동 종료)")
            await asyncio.sleep(8)
            await browser.close()

async def main():
    """메인 테스트 함수"""
    result = await test_visitor_toggle_button()
    
    print("\n" + "=" * 70)
    print("📊 방문차량 토글 버튼 테스트 결과")
    print("=" * 70)
    
    if isinstance(result, dict):
        print("📋 상세 분석:")
        print(f"   🔢 대시보드 카운터: {result['dashboard_count']}개")
        print(f"   🖱️ 토글 버튼 클릭 가능: {'YES' if result['toggle_clickable'] else 'NO'}")
        print(f"   📡 API 호출 감지: {'YES' if result['api_calls_detected'] else 'NO'}")
        print(f"   📋 표시 결과: {result['display_result']}")
        
        if result['display_result'] == 'no_vehicles_message':
            print(f"\n🎯 문제 확인:")
            print(f"   ❌ 대시보드는 {result['dashboard_count']}개 표시하지만 토글 버튼 클릭 시 '등록된 방문차량이 없습니다'")
            print(f"   💡 원인: API가 빈 데이터 반환 (VisitorVehicle vs VisitorReservation 모델 불일치)")
            print(f"   🔧 해결: 서버에서 API 수정 필요")
            
        elif result['display_result'] == 'vehicles_displayed':
            print(f"\n🎉 문제 해결됨:")
            print(f"   ✅ 방문차량 토글 버튼이 정상 작동합니다!")
            
    else:
        print("❌ 테스트 실행 실패")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())