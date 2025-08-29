#!/usr/bin/env python3
"""
API Diagnostic Script - Run this on the server to verify API implementation
Upload this to /tmp/ on the server and run: python3 api_diagnostic_script.py
"""

import os
import sys
import django
from datetime import date

def setup_django():
    """Setup Django environment"""
    try:
        sys.path.append('/home/kyb9852/vehicle-management-system')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def diagnose_api():
    """Diagnose the current API implementation"""
    
    print("🔍 API 진단 스크립트")
    print("=" * 50)
    
    if not setup_django():
        return
    
    from django.contrib.auth import get_user_model
    from visitors.models import VisitorReservation
    
    try:
        from vehicles.models import VisitorVehicle
        visitor_vehicle_available = True
    except ImportError:
        visitor_vehicle_available = False
        VisitorVehicle = None
    
    User = get_user_model()
    
    print("📊 모델 가용성:")
    print(f"   VisitorReservation: ✅")
    print(f"   VisitorVehicle: {'✅' if visitor_vehicle_available else '❌'}")
    
    # 1. 테스트 사용자 확인
    try:
        user = User.objects.get(username='newtest1754832743')
        print(f"\n👤 테스트 사용자:")
        print(f"   사용자: {user.username}")
        print(f"   타입: {user.user_type}")
        print(f"   아파트: {user.apartment}")
    except User.DoesNotExist:
        print("\n❌ 테스트 사용자를 찾을 수 없습니다")
        return
    
    # 2. VisitorReservation 데이터 확인
    today = date.today()
    
    all_reservations = VisitorReservation.objects.all()
    print(f"\n📋 VisitorReservation 데이터:")
    print(f"   전체: {all_reservations.count()}개")
    
    if all_reservations.exists():
        recent_reservations = all_reservations.order_by('-created_at')[:3]
        print(f"   최근 등록:")
        for i, res in enumerate(recent_reservations, 1):
            print(f"      {i}. {res.vehicle_number} - {res.visitor_name}")
            print(f"         날짜: {res.visit_date}, 승인: {res.is_approved}")
            print(f"         등록자: {res.resident.username}")
    
    # 3. API 로직 시뮬레이션
    print(f"\n🛠️ API 로직 시뮬레이션:")
    print(f"   기준 날짜: {today}")
    
    if user.user_type in ['admin', 'super_admin', 'main_account']:
        apartment = user.apartment
        if apartment:
            # 대시보드와 동일한 로직
            api_reservations = VisitorReservation.objects.filter(
                resident__apartment=apartment,
                visit_date__gte=today,
                is_approved=True
            ).select_related('resident').order_by('-created_at')
            
            print(f"   메인아이디 로직 결과: {api_reservations.count()}개")
            
            if api_reservations.exists():
                print(f"   ✅ 찾은 방문차량:")
                for res in api_reservations:
                    print(f"      - {res.vehicle_number} ({res.visitor_name})")
                    print(f"        날짜: {res.visit_date}, 등록자: {res.resident.username}")
            else:
                print(f"   ❌ 조건에 맞는 방문차량 없음")
                
                # 단계별 필터링 디버깅
                print(f"   🔍 단계별 필터링:")
                
                step1 = VisitorReservation.objects.filter(resident__apartment=apartment)
                print(f"      1단계 - 아파트별: {step1.count()}개")
                
                step2 = step1.filter(visit_date__gte=today)
                print(f"      2단계 - 오늘 이후: {step2.count()}개")
                
                step3 = step2.filter(is_approved=True)
                print(f"      3단계 - 승인된 것: {step3.count()}개")
    
    # 4. VisitorVehicle 데이터 확인 (구현 확인용)
    if visitor_vehicle_available and VisitorVehicle:
        visitor_vehicles = VisitorVehicle.objects.all()
        print(f"\n🚗 VisitorVehicle 데이터:")
        print(f"   전체: {visitor_vehicles.count()}개")
        
        if visitor_vehicles.exists():
            for i, vv in enumerate(visitor_vehicles[:2], 1):
                print(f"      {i}. {vv.vehicle_number}")
    else:
        print(f"\n🚗 VisitorVehicle: 사용 불가 또는 데이터 없음")
    
    # 5. 대시보드 카운터 로직 재현
    print(f"\n📊 대시보드 카운터 로직 재현:")
    
    if user.apartment:
        dashboard_count = VisitorReservation.objects.filter(
            resident__apartment=user.apartment,
            visit_date__gte=today,
            is_approved=True
        ).count()
        print(f"   대시보드 카운터: {dashboard_count}개")
    
    print(f"\n✅ 진단 완료!")
    print(f"\n💡 권장 사항:")
    print(f"   - API가 VisitorReservation 모델을 사용하도록 수정")
    print(f"   - 메인아이디는 아파트별 필터링 적용")
    print(f"   - visit_date__gte=today 조건 유지")

if __name__ == "__main__":
    diagnose_api()