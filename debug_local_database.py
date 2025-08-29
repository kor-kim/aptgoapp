#!/usr/bin/env python3
"""
Debug local database to understand why API returns 0 vehicles
"""

import os
import sys
import django
from datetime import date

# Django 설정
sys.path.append('/Users/dragonship/파이썬/ANPR')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from visitors.models import VisitorReservation

User = get_user_model()

def debug_local_database():
    """디버그 로컬 데이터베이스 상태"""
    
    print("🔍 로컬 데이터베이스 디버깅")
    print("=" * 60)
    
    # 1. 테스트 사용자 확인
    try:
        user = User.objects.get(username='newtest1754832743')
        print(f"✅ 사용자 정보:")
        print(f"   👤 사용자명: {user.username}")
        print(f"   🏢 아파트: {user.apartment}")
        print(f"   📱 사용자 타입: {user.user_type}")
        print(f"   ✅ 활성: {user.is_active}")
        print(f"   ✅ 승인: {getattr(user, 'is_approved', 'N/A')}")
        
    except User.DoesNotExist:
        print("❌ 테스트 사용자를 찾을 수 없습니다")
        return
    
    print()
    
    # 2. 전체 VisitorReservation 확인
    all_reservations = VisitorReservation.objects.all()
    print(f"📊 전체 VisitorReservation: {all_reservations.count()}개")
    
    if all_reservations.exists():
        print("   📋 최근 등록 5개:")
        for i, reservation in enumerate(all_reservations.order_by('-created_at')[:5], 1):
            print(f"      {i}. 차량: {reservation.vehicle_number}")
            print(f"         방문자: {reservation.visitor_name}")
            print(f"         날짜: {reservation.visit_date}")
            print(f"         승인: {reservation.is_approved}")
            print(f"         등록자: {reservation.resident.username}")
            print()
    
    # 3. API 필터링 로직 재현
    today = date.today()
    print(f"📅 오늘 날짜: {today}")
    
    if user.user_type in ['admin', 'super_admin', 'main_account']:
        print(f"🎯 메인아이디 로직 적용")
        apartment = user.apartment
        print(f"   🏢 사용자 아파트: {apartment}")
        
        if apartment:
            # API와 동일한 필터링
            api_reservations = VisitorReservation.objects.filter(
                resident__apartment=apartment,
                visit_date__gte=today,
                is_approved=True
            ).select_related('resident').order_by('-created_at')
            
            print(f"   📊 API 필터링 결과: {api_reservations.count()}개")
            
            if api_reservations.exists():
                print(f"   ✅ API 필터링으로 발견된 차량들:")
                for reservation in api_reservations:
                    print(f"      - {reservation.vehicle_number} ({reservation.visitor_name})")
                    print(f"        등록자: {reservation.resident.username}")
                    print(f"        아파트: {reservation.resident.apartment}")
                    print(f"        방문날짜: {reservation.visit_date}")
                    print(f"        승인여부: {reservation.is_approved}")
            else:
                print(f"   ❌ API 필터링 결과 없음")
                
                # 단계별 디버깅
                print(f"   🔍 단계별 필터링 디버깅:")
                
                # 아파트별 필터만
                step1 = VisitorReservation.objects.filter(resident__apartment=apartment)
                print(f"      1단계 - 아파트별: {step1.count()}개")
                
                # 날짜 필터 추가
                step2 = step1.filter(visit_date__gte=today)
                print(f"      2단계 - 오늘 이후: {step2.count()}개")
                
                # 승인 필터 추가
                step3 = step2.filter(is_approved=True)
                print(f"      3단계 - 승인된 것: {step3.count()}개")
                
                if step1.exists():
                    print(f"   📋 아파트별 전체 레코드:")
                    for reservation in step1.order_by('-created_at'):
                        print(f"      - {reservation.vehicle_number}")
                        print(f"        날짜: {reservation.visit_date} (기준: {today})")
                        print(f"        승인: {reservation.is_approved}")
                        print(f"        등록자 아파트: {reservation.resident.apartment}")
        else:
            print(f"   ❌ 사용자 아파트 정보 없음")
    else:
        print(f"🎯 부아이디 로직 적용")
        user_reservations = VisitorReservation.objects.filter(
            resident=user,
            visit_date__gte=today,
            is_approved=True
        )
        print(f"   📊 본인 등록 차량: {user_reservations.count()}개")

if __name__ == "__main__":
    debug_local_database()