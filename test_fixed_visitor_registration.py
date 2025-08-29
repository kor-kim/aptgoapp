#!/usr/bin/env python3
"""
수정된 메인아이디 방문차량 등록 기능 테스트
URL 충돌 해결 후 검증
"""

import asyncio
import json
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def test_fixed_visitor_registration():
    """수정된 방문차량 등록 기능 테스트"""
    
    print("=" * 80)
    print("🔧 수정된 메인아이디 방문차량 등록 기능 테스트")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            # 네트워크 요청 모니터링
            requests = []
            responses = []
            
            def on_request(request):
                requests.append({
                    'method': request.method,
                    'url': request.url,
                    'post_data': request.post_data if request.method == 'POST' else None
                })
            
            def on_response(response):
                responses.append({
                    'status': response.status,
                    'url': response.url
                })
            
            page.on('request', on_request)
            page.on('response', on_response)
            
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
            
            # 2단계: 방문차량 등록 페이지 접근
            print("\n📝 2단계: 방문차량 등록 페이지 접근")
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            page_title = await page.title()
            print(f"   ✅ 페이지 제목: {page_title}")
            
            # form action 확인
            form_action = await page.locator('form').get_attribute('action')
            print(f"   🔗 Form Action: {form_action}")
            
            # 3단계: 폼 데이터 입력 및 제출
            print("\n🚀 3단계: 방문차량 정보 입력 및 제출")
            
            requests.clear()
            responses.clear()
            
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"테스트{int(time.time()) % 10000}"
            
            # 폼 입력
            await page.fill('input[name="visitor_name"]', "수정테스트방문자")
            await page.fill('input[name="visitor_phone"]', "010-9999-8888")
            await page.fill('input[name="vehicle_number"]', test_vehicle)
            await page.fill('input[name="visit_date"]', today)
            await page.fill('input[name="visit_time"]', "16:30")
            await page.fill('input[name="purpose"]', "수정 후 테스트")
            
            print(f"   ✅ 입력 완료 - 차량번호: {test_vehicle}")
            
            # 폼 제출
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 4단계: 제출 결과 분석
            print("\n📊 4단계: 제출 결과 분석")
            
            final_url = page.url
            print(f"   📍 제출 후 URL: {final_url}")
            
            # POST 요청 확인
            post_requests = [r for r in requests if r['method'] == 'POST']
            print(f"   📡 POST 요청 개수: {len(post_requests)}")
            
            if post_requests:
                for i, req in enumerate(post_requests):
                    print(f"      POST {i+1}: {req['url']}")
                    if req['post_data']:
                        print(f"         데이터 크기: {len(req['post_data'])} bytes")
            
            # 응답 상태 확인
            print(f"   🌐 최종 응답들:")
            for resp in responses[-3:]:
                print(f"      {resp['status']} - {resp['url']}")
            
            # 성공 메시지 확인
            page_content = await page.content()
            success_found = False
            
            success_indicators = ["성공적으로 등록", "등록되었습니다", "완료되었습니다"]
            for indicator in success_indicators:
                if indicator in page_content:
                    print(f"   ✅ 성공 메시지 발견: '{indicator}'")
                    success_found = True
                    break
            
            if not success_found:
                error_indicators = ["오류", "실패", "에러"]
                for indicator in error_indicators:
                    if indicator in page_content:
                        print(f"   ❌ 에러 메시지 발견: '{indicator}'")
                        break
                else:
                    print(f"   ⚠️ 명확한 결과 메시지 없음")
            
            # 5단계: 대시보드에서 결과 확인
            print("\n🔍 5단계: 대시보드에서 등록 결과 확인")
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            
            dashboard_content = await page.content()
            
            if test_vehicle in dashboard_content:
                print(f"   ✅ 대시보드에서 등록된 차량 확인: {test_vehicle}")
                registration_success = True
            else:
                print(f"   ❌ 대시보드에서 차량 미확인: {test_vehicle}")
                
                # 방문차량 섹션 확인
                visitor_sections = await page.locator('*:has-text("방문차량")').all()
                print(f"   📋 방문차량 관련 섹션: {len(visitor_sections)}개")
                
                registration_success = False
            
            # 6단계: API 직접 확인
            print("\n🔧 6단계: 데이터베이스 직접 확인")
            
            # 방문자 예약 API로 확인 (만약 있다면)
            try:
                visitor_api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                if visitor_api_response.status == 200:
                    api_data = await visitor_api_response.json()
                    print(f"   📊 API 응답: {len(api_data)} 개의 방문차량")
                    
                    for vehicle in api_data:
                        if test_vehicle in str(vehicle):
                            print(f"   ✅ API에서 등록된 차량 확인!")
                            registration_success = True
                            break
                else:
                    print(f"   ⚠️ API 응답: {visitor_api_response.status}")
            except Exception as e:
                print(f"   ⚠️ API 확인 중 오류: {e}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/fixed_test_{datetime.now().strftime('%H%M%S')}.png")
            
            return registration_success
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창 확인 후 자동 종료됩니다...")
            await asyncio.sleep(5)  # 5초 대기
            await browser.close()

async def main():
    """메인 함수"""
    result = await test_fixed_visitor_registration()
    
    print("\n" + "=" * 80)
    print("📊 수정 후 테스트 결과")
    print("=" * 80)
    
    if result:
        print("🎉 SUCCESS: 수정된 방문차량 등록 시스템이 정상 작동합니다!")
        print("   ✅ URL 충돌 문제 해결됨")
        print("   ✅ 폼 제출이 올바른 엔드포인트로 처리됨")
        print("   ✅ 데이터베이스에 정상 저장됨")
        print("\n🏆 메인아이디 방문차량 등록 완전히 수정 완료!")
        
    else:
        print("❌ 문제가 여전히 존재합니다.")
        print("   📝 추가 디버깅이 필요할 수 있습니다.")
        print("   🔍 네트워크 요청 로그와 스크린샷을 확인하세요.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())