#!/usr/bin/env python3
"""
메인아이디 방문차량 등록 기능 테스트 및 분석
Playwright를 사용하여 직접 브라우저에서 테스트
"""

import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright

async def test_main_account_visitor_registration():
    """메인아이디의 방문차량 등록 기능 테스트"""
    
    print("=" * 70)
    print("🚗 메인아이디 방문차량 등록 기능 테스트")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    async with async_playwright() as p:
        # 브라우저 시작 (헤드풀 모드로 실행하여 UI 확인 가능)
        browser = await p.chromium.launch(
            headless=False,  # 브라우저 창을 보여주어 직접 확인 가능
            slow_mo=1000,    # 각 동작 사이 1초 지연
            args=['--start-maximized']
        )
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)  # 30초 타임아웃
            
            # 1단계: 로그인 페이지 접근
            print("📱 1단계: 로그인 페이지 접근")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            print(f"   ✅ 현재 URL: {page.url}")
            title = await page.title()
            print(f"   ✅ 페이지 제목: {title}")
            
            # 스크린샷 저장
            await page.screenshot(path="screenshots/01_login_page.png")
            
            # 2단계: 메인아이디로 로그인
            print("🔐 2단계: 메인아이디 로그인")
            
            # 아이디 입력
            username_field = page.locator('input[name="username"], input[id="username"], input[type="text"]').first
            await username_field.fill("newtest1754832743")
            print(f"   ✅ 아이디 입력 완료: newtest1754832743")
            
            # 비밀번호 입력  
            password_field = page.locator('input[name="password"], input[id="password"], input[type="password"]').first
            await password_field.fill("admin123")
            print(f"   ✅ 비밀번호 입력 완료")
            
            # 로그인 버튼 클릭
            login_button = page.locator('button[type="submit"], input[type="submit"], button:has-text("로그인")').first
            await login_button.click()
            print(f"   ✅ 로그인 버튼 클릭")
            
            # 로그인 완료 대기
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 추가 대기
            
            current_url = page.url
            print(f"   ✅ 로그인 후 URL: {current_url}")
            
            # 로그인 성공 확인
            if "dashboard" in current_url or "main-account" in current_url:
                print(f"   ✅ 로그인 성공!")
                await page.screenshot(path="screenshots/02_after_login.png")
            else:
                print(f"   ❌ 로그인 실패 - 예상치 못한 URL: {current_url}")
                await page.screenshot(path="screenshots/02_login_failed.png")
                return False
            
            # 3단계: 대시보드 분석
            print("📊 3단계: 메인아이디 대시보드 분석")
            
            # 페이지 내용 분석
            page_content = await page.content()
            
            # 방문차량 관련 요소 찾기
            visitor_links = await page.locator('a:has-text("방문"), a:has-text("visitor"), a:has-text("방문차량")').all()
            visitor_buttons = await page.locator('button:has-text("방문"), button:has-text("visitor"), button:has-text("방문차량")').all()
            
            print(f"   📋 방문차량 관련 링크 수: {len(visitor_links)}")
            print(f"   📋 방문차량 관련 버튼 수: {len(visitor_buttons)}")
            
            # 각 링크/버튼의 텍스트와 URL 확인
            for i, link in enumerate(visitor_links):
                text = await link.inner_text()
                href = await link.get_attribute('href')
                print(f"   🔗 방문차량 링크 {i+1}: '{text}' → {href}")
            
            for i, button in enumerate(visitor_buttons):
                text = await button.inner_text()
                print(f"   🔘 방문차량 버튼 {i+1}: '{text}'")
            
            # 네비게이션 메뉴 분석
            nav_links = await page.locator('nav a, .navbar a, .menu a').all()
            print(f"   📋 네비게이션 링크 총 {len(nav_links)}개:")
            for i, nav_link in enumerate(nav_links[:10]):  # 처음 10개만 표시
                try:
                    text = await nav_link.inner_text()
                    href = await nav_link.get_attribute('href')
                    if text.strip():
                        print(f"   📍 네비 {i+1}: '{text.strip()}' → {href}")
                except:
                    continue
            
            # 4단계: 방문차량 등록 기능 접근 시도
            print("🚗 4단계: 방문차량 등록 기능 접근 시도")
            
            # 직접 방문차량 등록 URL 시도
            register_urls = [
                "https://aptgo.org/register-visitor-vehicle/",
                "https://aptgo.org/visitor-register/",
                "https://aptgo.org/visitor/register/",
                "https://aptgo.org/accounts/register-visitor-vehicle/"
            ]
            
            visitor_registration_found = False
            working_url = None
            
            for url in register_urls:
                try:
                    print(f"   🔍 시도 중: {url}")
                    await page.goto(url)
                    await page.wait_for_load_state('networkidle')
                    
                    current_url = page.url
                    page_title = await page.title()
                    
                    # 404나 에러 페이지가 아닌지 확인
                    if "404" not in page_title and "Not Found" not in page_title and "오류" not in page_title:
                        print(f"   ✅ 접근 성공: {url}")
                        print(f"   📋 페이지 제목: {page_title}")
                        
                        # 방문차량 등록 폼이 있는지 확인
                        form_elements = await page.locator('form').all()
                        input_elements = await page.locator('input[type="text"], input[type="tel"], input[name*="plate"], input[name*="vehicle"]').all()
                        
                        print(f"   📝 폼 개수: {len(form_elements)}")
                        print(f"   📋 입력 필드 개수: {len(input_elements)}")
                        
                        if len(form_elements) > 0 or len(input_elements) > 0:
                            visitor_registration_found = True
                            working_url = url
                            await page.screenshot(path=f"screenshots/03_visitor_registration_{url.split('/')[-2]}.png")
                            break
                        else:
                            print(f"   ⚠️ 폼이 없는 페이지")
                    else:
                        print(f"   ❌ 404 또는 에러 페이지: {page_title}")
                        
                except Exception as e:
                    print(f"   ❌ 접근 실패: {e}")
                    continue
            
            # 5단계: 권한 및 기능 분석
            print("🔍 5단계: 권한 및 기능 분석")
            
            if visitor_registration_found:
                print(f"   ✅ 방문차량 등록 페이지 발견: {working_url}")
                
                # 폼 필드 분석
                await page.goto(working_url)
                await page.wait_for_load_state('networkidle')
                
                # 입력 필드 확인
                plate_inputs = await page.locator('input[name*="plate"], input[name*="number"], input[placeholder*="차량"], input[placeholder*="번호"]').all()
                name_inputs = await page.locator('input[name*="name"], input[name*="owner"], input[placeholder*="이름"], input[placeholder*="소유"]').all()
                phone_inputs = await page.locator('input[name*="phone"], input[name*="tel"], input[type="tel"], input[placeholder*="연락"], input[placeholder*="전화"]').all()
                
                print(f"   🚗 차량번호 입력 필드: {len(plate_inputs)}개")
                print(f"   👤 이름 입력 필드: {len(name_inputs)}개") 
                print(f"   📞 연락처 입력 필드: {len(phone_inputs)}개")
                
                # 테스트 데이터 입력 시도
                if len(plate_inputs) > 0:
                    test_plate = f"서울12가{int(time.time()) % 10000}"
                    await plate_inputs[0].fill(test_plate)
                    print(f"   ✅ 테스트 차량번호 입력: {test_plate}")
                
                if len(name_inputs) > 0:
                    await name_inputs[0].fill("테스트방문자")
                    print(f"   ✅ 테스트 이름 입력: 테스트방문자")
                
                if len(phone_inputs) > 0:
                    await phone_inputs[0].fill("010-1234-5678")
                    print(f"   ✅ 테스트 연락처 입력: 010-1234-5678")
                
                await page.screenshot(path="screenshots/04_visitor_form_filled.png")
                
                # 제출 버튼 확인 (실제 제출하지는 않음)
                submit_buttons = await page.locator('button[type="submit"], input[type="submit"], button:has-text("등록"), button:has-text("저장"), button:has-text("추가")').all()
                print(f"   🔘 제출 버튼: {len(submit_buttons)}개")
                
                for i, button in enumerate(submit_buttons):
                    text = await button.inner_text()
                    print(f"   📝 제출 버튼 {i+1}: '{text}'")
                
            else:
                print(f"   ❌ 방문차량 등록 페이지를 찾을 수 없음")
                print(f"   📋 확인된 기능 부재 - 메인아이디는 방문차량 등록 권한이 없는 것으로 추정")
            
            # 6단계: 부아이디 기능과 비교 분석
            print("🔄 6단계: 부아이디 기능과 비교 분석")
            
            # 부아이디 관련 페이지 접근해서 차이점 확인
            try:
                await page.goto("https://aptgo.org/manage-sub-accounts/")
                await page.wait_for_load_state('networkidle')
                
                sub_account_title = await page.title()
                print(f"   📋 부아이디 관리 페이지: {sub_account_title}")
                
                # 부아이디 관리 페이지에서 방문차량 관련 기능 확인
                sub_visitor_elements = await page.locator('*:has-text("방문"), *:has-text("visitor")').all()
                print(f"   🔍 부아이디 페이지의 방문차량 관련 요소: {len(sub_visitor_elements)}개")
                
                await page.screenshot(path="screenshots/05_sub_account_management.png")
                
            except Exception as e:
                print(f"   ⚠️ 부아이디 페이지 접근 실패: {e}")
            
            # 최종 결과 정리
            print("\n" + "=" * 70)
            print("📊 분석 결과 요약")
            print("=" * 70)
            
            if visitor_registration_found:
                print("✅ 메인아이디 방문차량 등록 기능: 존재함")
                print(f"   🔗 접근 URL: {working_url}")
                print("   📝 필요한 개선사항: 폼 필드 및 UI 최적화")
            else:
                print("❌ 메인아이디 방문차량 등록 기능: 부재")
                print("   📝 필요한 작업: 방문차량 등록 기능 구현 필요")
                print("   🎯 목표: 부아이디와 동일한 방문차량 등록 권한 부여")
            
            return visitor_registration_found
            
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
            await page.screenshot(path="screenshots/error_occurred.png")
            return False
            
        finally:
            # 브라우저는 자동으로 닫지 않음 (수동 확인을 위해)
            print("\n🔍 브라우저 창이 열려있습니다. 수동으로 추가 확인 후 닫아주세요.")
            print("Press Enter to close browser...")
            input()  # 사용자 입력 대기
            await browser.close()

async def main():
    """메인 함수"""
    result = await test_main_account_visitor_registration()
    
    if result:
        print("\n🎉 테스트 완료: 메인아이디 방문차량 등록 기능이 존재함")
        print("   📝 다음 단계: UI 개선 및 접근성 향상")
    else:
        print("\n⚠️ 테스트 완료: 메인아이디 방문차량 등록 기능 부재 확인")
        print("   📝 다음 단계: 방문차량 등록 기능 구현 필요")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())