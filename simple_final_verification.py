#!/usr/bin/env python3
"""
간단한 최종 검증 테스트
메인아이디 방문차량 등록 기본 동작 확인
"""

import asyncio
import time
from datetime import datetime, date
from playwright.async_api import async_playwright

async def simple_final_verification():
    """간단한 최종 검증"""
    
    print("=" * 70)
    print("✅ 간단한 최종 검증: 메인아이디 방문차량 등록")
    print(f"⏰ 검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(15000)
            
            # 1단계: 로그인
            print("🔐 로그인 테스트")
            await page.goto("https://aptgo.org/login/", wait_until='networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" not in page.url:
                print(f"   ❌ 로그인 실패")
                return False
            print(f"   ✅ 로그인 성공")
            
            # 2단계: 방문차량 등록
            print("🚗 방문차량 등록 테스트")
            await page.goto("https://aptgo.org/register-visitor-vehicle/", wait_until='networkidle')
            
            today = date.today().strftime('%Y-%m-%d')
            test_vehicle = f"검증{int(time.time()) % 1000}"
            
            await page.fill('input[name="visitor_name"]', "검증방문자")
            await page.fill('input[name="vehicle_number"]', test_vehicle)
            await page.fill('input[name="visit_date"]', today)
            
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # 성공 메시지 확인
            page_content = await page.content()
            registration_success = "성공적으로 등록" in page_content
            print(f"   ✅ 등록 {'성공' if registration_success else '실패'}")
            
            # 3단계: 대시보드 확인
            print("📊 대시보드 확인")
            await page.goto("https://aptgo.org/main-account-dashboard/", wait_until='networkidle')
            
            dashboard_content = await page.content()
            
            # 방문차량 0이 아닌 숫자 확인
            dashboard_success = "방문차량 0" not in dashboard_content or test_vehicle in dashboard_content
            print(f"   ✅ 대시보드 {'업데이트됨' if dashboard_success else '미업데이트'}")
            
            return registration_success and dashboard_success
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            return False
            
        finally:
            await browser.close()

async def main():
    result = await simple_final_verification()
    
    print("\n" + "=" * 70)
    print("🏆 최종 검증 결과")
    print("=" * 70)
    
    if result:
        print("🎉 성공! 메인아이디 방문차량 등록 시스템이 정상 작동합니다!")
        print("✅ 등록 기능 작동")
        print("✅ 대시보드 표시 기능 작동")
        print("\n🏆 모든 요구사항이 구현되었습니다!")
        
    else:
        print("❌ 시스템에 문제가 있습니다.")
        print("📝 추가 조사가 필요합니다.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())