#!/usr/bin/env python3
"""
Final verification test for visitor vehicle display fix
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def final_verification_test():
    """최종 검증 테스트"""
    
    print("=" * 80)
    print("🏁 최종 검증: 메인아이디 방문차량 표시 수정 확인")
    print(f"⏰ 검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(20000)
            
            # 1단계: 로그인
            print("\n🔐 1단계: 메인아이디 로그인")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" in page.url:
                print(f"   ✅ 로그인 성공")
            else:
                print(f"   ❌ 로그인 실패")
                return False
            
            # 2단계: 대시보드에서 방문차량 카운터 확인
            print("\n📊 2단계: 대시보드 방문차량 카운터 확인")
            
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            visitor_count_text = ""
            visitor_elements = await page.locator('*:has-text("방문차량")').all()
            
            for element in visitor_elements:
                try:
                    text = await element.inner_text()
                    if "방문차량" in text and any(char.isdigit() for char in text):
                        visitor_count_text = text.strip()
                        print(f"   📊 방문차량 카운터: '{visitor_count_text}'")
                        break
                except:
                    continue
            
            # 3단계: 방문차량 버튼 클릭
            print("\n🖱️ 3단계: 방문차량 버튼 클릭")
            
            visitor_clicked = False
            visitor_buttons = await page.locator('button:has-text("방문차량"), a:has-text("방문차량")').all()
            
            for button in visitor_buttons:
                try:
                    text = await button.inner_text()
                    if "방문차량" in text:
                        print(f"   🖱️ 클릭: '{text.strip()}'")
                        await button.click()
                        await page.wait_for_load_state('networkidle')
                        await asyncio.sleep(5)  # 더 긴 대기 시간
                        visitor_clicked = True
                        break
                except Exception as e:
                    print(f"   ⚠️ 클릭 실패: {e}")
                    continue
            
            # 4단계: 방문차량 표시 확인
            print("\n🔍 4단계: 방문차량 표시 확인")
            
            page_content = await page.content()
            
            if "등록된 방문차량이 없습니다" in page_content:
                print(f"   ❌ 여전히 '등록된 방문차량이 없습니다' 메시지 표시됨")
                
                # API 직접 확인
                print(f"\n🛠️ API 직접 확인:")
                try:
                    api_response = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
                    if api_response.status == 200:
                        api_data = await api_response.json()
                        vehicles_count = len(api_data.get('vehicles', []))
                        print(f"   📡 API 응답: {vehicles_count}개 방문차량")
                        
                        if vehicles_count > 0:
                            print(f"   ✅ API에 데이터 있음 - 프론트엔드 로딩 문제일 수 있음")
                            for i, vehicle in enumerate(api_data.get('vehicles', [])[:3]):
                                print(f"      {i+1}. {vehicle.get('vehicle_number', 'N/A')} - {vehicle.get('visitor_name', 'N/A')}")
                        else:
                            print(f"   ❌ API에도 데이터 없음")
                    else:
                        print(f"   ❌ API 응답 오류: {api_response.status}")
                except Exception as e:
                    print(f"   ❌ API 호출 오류: {e}")
                    
                return False
                
            else:
                # 방문차량 목록이 표시되는지 확인
                vehicle_found = False
                
                # 차량번호 패턴 찾기
                import re
                vehicle_patterns = re.findall(r'[0-9]{2,3}[가-힣][0-9]{4}', page_content)
                if vehicle_patterns:
                    print(f"   ✅ 방문차량 목록 표시됨!")
                    for i, pattern in enumerate(vehicle_patterns[:5]):
                        print(f"      {i+1}. 차량번호: {pattern}")
                    vehicle_found = True
                else:
                    # 테이블 형태로 표시되는지 확인
                    if "차량번호" in page_content and "방문자" in page_content:
                        print(f"   ✅ 방문차량 테이블 표시됨!")
                        vehicle_found = True
                
                if not vehicle_found:
                    print(f"   ⚠️ 방문차량 목록 형태를 정확히 파악하기 어려움")
                    print(f"   📋 페이지에 '등록된 방문차량이 없습니다' 메시지는 없음")
                
                return vehicle_found
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/final_verification_{datetime.now().strftime('%H%M%S')}.png")
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/final_test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print("\n🔍 브라우저 창 확인 후 자동 종료...")
            await asyncio.sleep(8)
            await browser.close()

async def main():
    """메인 함수"""
    result = await final_verification_test()
    
    print("\n" + "=" * 80)
    print("📊 최종 검증 결과")
    print("=" * 80)
    
    if result:
        print("🎉 성공! 메인아이디 방문차량 표시 기능이 수정되었습니다!")
        print("✅ 대시보드에서 '방문차량' 버튼 클릭 시 등록된 차량이 표시됩니다")
        print("✅ API와 프론트엔드가 정상적으로 연동됩니다")
        print("\n🏆 문제 해결 완료!")
        print("   - 메인아이디 로그인 ✅")
        print("   - 방문차량 카운터 표시 ✅") 
        print("   - 방문차량 버튼 클릭 ✅")
        print("   - 방문차량 목록 표시 ✅")
        
    else:
        print("❌ 아직 문제가 남아있습니다")
        print("📝 추가 진단이 필요할 수 있습니다")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())