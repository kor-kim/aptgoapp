#!/usr/bin/env python3
"""
메인아이디 방문차량 등록 기능 최종 검증 테스트
완전한 폼 제출 과정까지 테스트
"""

import asyncio
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def test_complete_visitor_registration():
    """메인아이디 방문차량 등록 완전 테스트 (폼 제출까지)"""
    
    print("=" * 70)
    print("🎯 메인아이디 방문차량 등록 완전 테스트")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless로 실행
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(15000)
            
            # 1단계: 로그인
            print("🔐 1단계: 메인아이디 로그인")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            # 로그인 정보 입력
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            current_url = page.url
            if "dashboard" not in current_url:
                print(f"   ❌ 로그인 실패: {current_url}")
                return False
            print(f"   ✅ 로그인 성공: {current_url}")
            
            # 2단계: 방문차량 등록 페이지 접근
            print("📝 2단계: 방문차량 등록 페이지 접근")
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            page_title = await page.title()
            print(f"   ✅ 페이지 제목: {page_title}")
            
            # 3단계: 폼 데이터 입력
            print("✍️ 3단계: 방문차량 정보 입력")
            
            # 현재 날짜 설정
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"서울12가{int(time.time()) % 10000}"
            
            # 폼 필드 입력
            await page.fill('input[name="visitor_name"]', "테스트방문자")
            print(f"   ✅ 방문자 이름: 테스트방문자")
            
            await page.fill('input[name="visitor_phone"]', "010-1234-5678") 
            print(f"   ✅ 방문자 연락처: 010-1234-5678")
            
            await page.fill('input[name="vehicle_number"]', test_vehicle)
            print(f"   ✅ 차량번호: {test_vehicle}")
            
            await page.fill('input[name="visit_date"]', today)
            print(f"   ✅ 방문날짜: {today}")
            
            await page.fill('input[name="visit_time"]', "14:30")
            print(f"   ✅ 방문시간: 14:30")
            
            await page.fill('input[name="purpose"]', "가족방문")
            print(f"   ✅ 방문목적: 가족방문")
            
            # 4단계: 폼 제출
            print("🚀 4단계: 방문차량 등록 제출")
            
            # 제출 버튼 클릭
            submit_button = page.locator('button[type="submit"]')
            await submit_button.click()
            print(f"   ✅ 등록 버튼 클릭")
            
            # 결과 대기
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 5단계: 결과 확인
            print("🔍 5단계: 등록 결과 확인")
            
            final_url = page.url
            page_content = await page.content()
            
            # 성공/실패 메시지 확인
            success_indicators = [
                "성공적으로 등록",
                "등록이 완료",
                "등록되었습니다", 
                "성공",
                "완료"
            ]
            
            error_indicators = [
                "오류",
                "실패", 
                "에러",
                "잘못",
                "ERROR"
            ]
            
            has_success = any(indicator in page_content for indicator in success_indicators)
            has_error = any(indicator in page_content for indicator in error_indicators)
            
            print(f"   📍 최종 URL: {final_url}")
            
            if has_success:
                print(f"   ✅ 등록 성공! 방문차량이 성공적으로 등록되었습니다.")
                registration_success = True
            elif has_error:
                print(f"   ❌ 등록 실패: 오류 메시지 발견")
                registration_success = False
            else:
                # 리다이렉트 확인 (등록 후 대시보드로 이동하는 경우)
                if "dashboard" in final_url:
                    print(f"   ✅ 등록 완료 (대시보드로 리다이렉트됨)")
                    registration_success = True
                else:
                    print(f"   ⚠️ 결과 불분명 - 수동 확인 필요")
                    registration_success = None
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/visitor_registration_final_{datetime.now().strftime('%H%M%S')}.png")
            
            return registration_success
            
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
            await page.screenshot(path=f"screenshots/visitor_registration_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            await browser.close()

async def main():
    """메인 함수"""
    result = await test_complete_visitor_registration()
    
    print("\n" + "=" * 70)
    print("📊 최종 테스트 결과")
    print("=" * 70)
    
    if result is True:
        print("🎉 SUCCESS: 메인아이디 방문차량 등록 기능이 완전히 작동합니다!")
        print("   ✅ 로그인 성공")
        print("   ✅ 방문차량 등록 페이지 접근 성공") 
        print("   ✅ 폼 입력 성공")
        print("   ✅ 등록 제출 성공")
        print("\n🏆 메인아이디도 부아이디처럼 방문차량 등록이 가능합니다!")
        
    elif result is False:
        print("❌ FAILURE: 방문차량 등록 과정에서 오류가 발생했습니다.")
        print("   📝 추가 디버깅이 필요할 수 있습니다.")
        
    else:
        print("⚠️ PARTIAL: 등록 과정은 완료되었으나 결과 확인이 필요합니다.")
        print("   📝 수동으로 대시보드에서 등록된 방문차량을 확인해주세요.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())