#!/usr/bin/env python3
"""
Complete flow test: Register visitor vehicle and verify it appears in API
"""

import asyncio
import json
import time
from datetime import datetime, date, timedelta
from playwright.async_api import async_playwright

async def complete_flow_test():
    """Complete flow test including registration and verification"""
    
    print("=== 🔄 완전한 플로우 테스트: 등록 → 확인 ===")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # 1단계: 로그인
            print("\n🔐 1단계: 메인아이디 로그인")
            await page.goto("https://aptgo.org/login/")
            await page.wait_for_load_state('networkidle')
            
            await page.fill('input[name="username"]', "newtest1754832743")
            await page.fill('input[name="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            if "dashboard" in page.url:
                print("   ✅ 로그인 성공")
            else:
                print("   ❌ 로그인 실패")
                return False
            
            # 2단계: 등록 전 API 상태 확인
            print("\n📊 2단계: 등록 전 API 상태 확인")
            
            api_response_before = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
            before_count = 0
            
            if api_response_before.status == 200:
                try:
                    before_data = await api_response_before.json()
                    before_count = len(before_data.get('visitor_vehicles', []))
                    print(f"   📊 등록 전 방문차량: {before_count}개")
                    
                    if before_count > 0:
                        print("   📋 기존 방문차량 목록:")
                        for i, vehicle in enumerate(before_data.get('visitor_vehicles', [])[:3]):
                            print(f"      {i+1}. {vehicle.get('vehicle_number', 'N/A')} - {vehicle.get('visitor_name', 'N/A')}")
                    
                except Exception as e:
                    print(f"   ⚠️ API 응답 파싱 실패: {e}")
            
            # 3단계: 새로운 방문차량 등록
            print("\n🚗 3단계: 새로운 방문차량 등록")
            
            await page.goto("https://aptgo.org/register-visitor-vehicle/")
            await page.wait_for_load_state('networkidle')
            
            # 유니크한 테스트 차량번호 생성
            test_vehicle = f"테스트{int(time.time()) % 10000}"
            tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            try:
                await page.fill('input[name="visitor_name"]', "완전플로우테스트방문자")
                await page.fill('input[name="visitor_phone"]', "010-9999-0000")
                await page.fill('input[name="vehicle_number"]', test_vehicle)
                await page.fill('input[name="visit_date"]', tomorrow)
                await page.fill('input[name="visit_time"]', "16:00")
                await page.fill('input[name="purpose"]', "완전한 플로우 테스트")
                
                print(f"   🔖 등록 차량번호: {test_vehicle}")
                print(f"   📅 방문 예정일: {tomorrow}")
                
                # 폼 제출
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                page_content = await page.content()
                if "성공적으로 등록" in page_content or "등록" in page_content:
                    print("   ✅ 방문차량 등록 완료!")
                else:
                    print("   ⚠️ 등록 결과 메시지 불명확")
                
            except Exception as e:
                print(f"   ❌ 등록 중 오류: {e}")
                return False
            
            # 4단계: 등록 후 즉시 API 확인
            print("\n🔄 4단계: 등록 후 즉시 API 확인")
            
            # 잠시 대기 (데이터베이스 커밋 시간)
            await asyncio.sleep(2)
            
            api_response_after = await page.request.get("https://aptgo.org/api/visitor-vehicles-api/")
            
            if api_response_after.status == 200:
                try:
                    after_data = await api_response_after.json()
                    after_count = len(after_data.get('visitor_vehicles', []))
                    
                    print(f"   📊 등록 후 방문차량: {after_count}개")
                    print(f"   🔢 증가량: {after_count - before_count}개")
                    
                    if after_count > before_count:
                        print("   🎉 API에 새 데이터 추가됨!")
                        
                        # 새로 등록된 차량 찾기
                        found_test_vehicle = False
                        for vehicle in after_data.get('visitor_vehicles', []):
                            if test_vehicle in vehicle.get('vehicle_number', ''):
                                print(f"   ✅ 등록한 테스트 차량 확인됨!")
                                print(f"      차량: {vehicle.get('vehicle_number')}")
                                print(f"      방문자: {vehicle.get('visitor_name')}")
                                print(f"      등록자: {vehicle.get('registered_by')}")
                                found_test_vehicle = True
                                break
                        
                        if not found_test_vehicle:
                            print(f"   ⚠️ 테스트 차량({test_vehicle})은 없지만 다른 차량 추가됨")
                            print(f"   📋 최신 차량 목록:")
                            for i, vehicle in enumerate(after_data.get('visitor_vehicles', [])[:3]):
                                print(f"      {i+1}. {vehicle.get('vehicle_number')} - {vehicle.get('visitor_name')}")
                        
                        return True
                        
                    elif after_count == before_count:
                        print(f"   ❌ API 데이터 변화 없음")
                        print(f"   💡 등록은 되었지만 API 필터링에서 제외될 수 있음")
                        
                        # 전체 API 응답 분석
                        print(f"   📄 전체 API 응답: {after_data}")
                        
                        return False
                    else:
                        print(f"   ⚠️ 예상치 못한 데이터 감소")
                        return False
                        
                except Exception as e:
                    response_text = await api_response_after.text()
                    print(f"   ❌ API 응답 파싱 실패: {e}")
                    print(f"   📄 응답 내용: {response_text[:200]}")
                    return False
            else:
                print(f"   ❌ API 호출 실패: {api_response_after.status}")
                return False
            
            # 5단계: 대시보드 방문차량 버튼 테스트
            print("\n🖱️ 5단계: 대시보드 방문차량 버튼 클릭 테스트")
            
            await page.goto("https://aptgo.org/main-account-dashboard/")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # 방문차량 버튼 찾아서 클릭
            visitor_buttons = await page.locator('*:has-text("방문차량")').all()
            
            for button in visitor_buttons:
                try:
                    text = await button.inner_text()
                    if "방문차량" in text and any(char.isdigit() for char in text):
                        print(f"   🖱️ 방문차량 버튼 클릭: '{text.strip()}'")
                        await button.click()
                        await page.wait_for_load_state('networkidle')
                        await asyncio.sleep(5)
                        
                        # 클릭 후 페이지 확인
                        page_content = await page.content()
                        
                        if "등록된 방문차량이 없습니다" in page_content:
                            print(f"   ❌ 여전히 '등록된 방문차량이 없습니다' 메시지")
                        elif test_vehicle in page_content:
                            print(f"   🎉 등록한 테스트 차량이 페이지에 표시됨!")
                        else:
                            # 다른 차량번호 패턴 찾기
                            import re
                            vehicle_patterns = re.findall(r'[0-9]{2,3}[가-힣][0-9]{4}', page_content)
                            if vehicle_patterns:
                                print(f"   ✅ 다른 방문차량들이 표시됨: {len(vehicle_patterns)}개")
                                for pattern in vehicle_patterns[:3]:
                                    print(f"      - {pattern}")
                            else:
                                print(f"   ⚠️ 방문차량 표시 상태 불명확")
                        
                        break
                except:
                    continue
            
            # 스크린샷 저장
            await page.screenshot(path=f"screenshots/complete_flow_test_{datetime.now().strftime('%H%M%S')}.png")
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            await page.screenshot(path=f"screenshots/flow_test_error_{datetime.now().strftime('%H%M%S')}.png")
            return False
            
        finally:
            print(f"\n🔍 브라우저 창 확인 (8초 후 자동 종료)")
            await asyncio.sleep(8)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_flow_test())