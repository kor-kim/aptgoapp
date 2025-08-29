#!/usr/bin/env python3
"""
메인아이디 방문차량 등록 문제 종합 진단
API 엔드포인트와 등록 프로세스 완전 분석
"""

import asyncio
import json
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def comprehensive_visitor_registration_test():
    """방문차량 등록 기능 종합 테스트"""
    
    print("=" * 80)
    print("🔍 메인아이디 방문차량 등록 종합 진단")
    print(f"⏰ 진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            # 네트워크 요청 모니터링 설정
            requests = []
            responses = []
            
            def on_request(request):
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data
                })
            
            def on_response(response):
                responses.append({
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers)
                })
            
            page.on('request', on_request)
            page.on('response', on_response)
            
            # 1단계: 로그인
            print("🔐 1단계: 메인아이디 로그인 테스트")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            current_url = page.url
            if "dashboard" not in current_url:
                print(f"   ❌ 로그인 실패: {current_url}")
                return False
            print(f"   ✅ 로그인 성공: {current_url}")
            
            # 2단계: 방문차량 등록 페이지들 테스트
            print("\n📝 2단계: 방문차량 등록 페이지 접근 테스트")
            
            # 2-1: /register-visitor-vehicle/ 테스트
            print("   🔗 2-1: /register-visitor-vehicle/ 테스트")
            try:
                await page.goto("https://aptgo.org/register-visitor-vehicle/")
                await page.wait_for_load_state('networkidle')
                page_title = await page.title()
                page_content = await page.content()
                
                if "방문차량 등록" in page_title or "방문차량" in page_content:
                    print(f"      ✅ 접근 성공: {page_title}")
                    
                    # 폼 요소 확인
                    form_count = await page.locator('form').count()
                    input_count = await page.locator('input').count()
                    print(f"      📝 폼 개수: {form_count}, 입력 필드 개수: {input_count}")
                else:
                    print(f"      ❌ 페이지 접근 실패 또는 내용 없음")
            except Exception as e:
                print(f"      ❌ 오류: {e}")
            
            # 2-2: /api/register-visitor/ 직접 테스트  
            print("   🔗 2-2: /api/register-visitor/ 직접 접근 테스트")
            try:
                await page.goto("https://aptgo.org/api/register-visitor/")
                await page.wait_for_load_state('networkidle')
                page_content = await page.content()
                
                if "405" in page_content or "Method Not Allowed" in page_content:
                    print(f"      ⚠️ GET 방식 접근 불가 (정상 - POST 전용 API)")
                elif "404" in page_content:
                    print(f"      ❌ API 엔드포인트 존재하지 않음")
                else:
                    print(f"      ✅ API 엔드포인트 접근 가능")
            except Exception as e:
                print(f"      ❌ API 접근 오류: {e}")
            
            # 3단계: 폼 제출 테스트 (두 가지 방식)
            print("\n🚀 3단계: 방문차량 등록 폼 제출 테스트")
            
            # 3-1: 기본 등록 페이지에서 제출
            print("   📋 3-1: /register-visitor-vehicle/ 페이지에서 제출")
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            # 요청/응답 로그 초기화
            requests.clear()
            responses.clear()
            
            # 테스트 데이터 입력
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"서울12가{int(time.time()) % 10000}"
            
            try:
                await page.fill('input[name="visitor_name"]', "테스트방문자")
                await page.fill('input[name="visitor_phone"]', "010-1234-5678")
                await page.fill('input[name="vehicle_number"]', test_vehicle)
                await page.fill('input[name="visit_date"]', today)
                await page.fill('input[name="visit_time"]', "15:00")
                await page.fill('input[name="purpose"]', "테스트목적")
                
                print(f"      ✅ 폼 데이터 입력 완료: {test_vehicle}")
                
                # 폼 제출
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # 제출 후 상태 확인
                final_url = page.url
                final_content = await page.content()
                
                print(f"      📍 제출 후 URL: {final_url}")
                
                # 네트워크 요청 분석
                print("      🌐 네트워크 요청 분석:")
                for req in requests[-5:]:  # 마지막 5개 요청만
                    print(f"         {req['method']} {req['url']}")
                
                print("      🌐 응답 분석:")
                for resp in responses[-5:]:  # 마지막 5개 응답만
                    print(f"         {resp['status']} {resp['url']}")
                
                # 성공/실패 판단
                if "성공" in final_content or "완료" in final_content:
                    print(f"      ✅ 등록 성공 메시지 확인")
                elif "오류" in final_content or "실패" in final_content:
                    print(f"      ❌ 등록 실패 메시지 확인")
                elif final_url != "https://aptgo.org/register-visitor-vehicle/":
                    print(f"      ✅ 페이지 리다이렉트 발생 (등록 완료 추정)")
                else:
                    print(f"      ⚠️ 결과 불분명")
                    
            except Exception as e:
                print(f"      ❌ 폼 제출 오류: {e}")
            
            # 4단계: 대시보드에서 등록 결과 확인
            print("\n📊 4단계: 대시보드에서 방문차량 등록 결과 확인")
            try:
                await page.goto("https://aptgo.org/main-account-dashboard/")
                await page.wait_for_load_state('networkidle')
                
                dashboard_content = await page.content()
                
                # 방문차량 관련 요소 찾기
                visitor_elements = await page.locator('*:has-text("방문차량"), *:has-text("visitor")').all()
                print(f"   📋 대시보드 방문차량 관련 요소: {len(visitor_elements)}개")
                
                for i, element in enumerate(visitor_elements[:3]):
                    try:
                        text = await element.inner_text()
                        print(f"      {i+1}. {text.strip()}")
                    except:
                        continue
                        
                # 등록된 차량 번호 검색
                if test_vehicle in dashboard_content:
                    print(f"   ✅ 등록된 차량번호 발견: {test_vehicle}")
                else:
                    print(f"   ❌ 등록된 차량번호 미발견: {test_vehicle}")
                    
            except Exception as e:
                print(f"   ❌ 대시보드 확인 오류: {e}")
            
            # 5단계: API 직접 호출 테스트
            print("\n🔧 5단계: API 직접 호출 테스트")
            try:
                # CSRF 토큰 획득
                await page.goto("https://aptgo.org/register-visitor-vehicle/")
                await page.wait_for_load_state('networkidle')
                
                csrf_token = await page.locator('input[name="csrfmiddlewaretoken"]').get_attribute('value')
                print(f"   🔐 CSRF 토큰 획득: {csrf_token[:20]}...")
                
                # API 데이터 준비
                api_data = {
                    'visitor_name': '직접API테스트',
                    'visitor_phone': '010-9999-8888',
                    'vehicle_number': f'서울99나{int(time.time()) % 1000}',
                    'visit_date': today,
                    'visit_time': '16:00',
                    'purpose': 'API테스트',
                    'csrfmiddlewaretoken': csrf_token
                }
                
                # API 호출
                api_response = await page.request.post(
                    "https://aptgo.org/api/register-visitor/",
                    data=api_data,
                    headers={
                        'Referer': 'https://aptgo.org/register-visitor-vehicle/',
                        'X-CSRFToken': csrf_token
                    }
                )
                
                print(f"   📡 API 응답 상태: {api_response.status}")
                
                if api_response.status == 200:
                    response_text = await api_response.text()
                    print(f"   ✅ API 호출 성공: {response_text[:100]}...")
                elif api_response.status == 404:
                    print(f"   ❌ API 엔드포인트 없음 (404)")
                elif api_response.status == 403:
                    print(f"   ❌ 권한 없음 (403) - 메인아이디 접근 제한")
                elif api_response.status == 405:
                    print(f"   ❌ 메서드 불허 (405)")
                else:
                    print(f"   ❌ API 호출 실패: {api_response.status}")
                    
            except Exception as e:
                print(f"   ❌ API 직접 호출 오류: {e}")
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/visitor_diagnosis_{datetime.now().strftime('%H%M%S')}.png")
            
            return True
            
        except Exception as e:
            print(f"❌ 전체 진단 과정 오류: {e}")
            await page.screenshot(path=f"screenshots/diagnosis_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창이 열려있습니다. 수동으로 추가 확인 후 닫아주세요.")
            print("Press Enter to close browser...")
            # input() 제거 - 자동 종료
            await asyncio.sleep(3)
            await browser.close()

async def main():
    """메인 함수"""
    print("🚀 방문차량 등록 시스템 종합 진단 시작")
    
    result = await comprehensive_visitor_registration_test()
    
    print("\n" + "=" * 80)
    print("📊 종합 진단 결과")
    print("=" * 80)
    
    if result:
        print("✅ 진단 프로세스 완료")
        print("📝 위의 분석 결과를 바탕으로 문제점을 파악하고 수정하겠습니다.")
    else:
        print("❌ 진단 프로세스 중 오류 발생")
        print("📝 수동 확인이 필요할 수 있습니다.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())