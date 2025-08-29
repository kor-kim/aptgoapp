#!/usr/bin/env python3
"""
Debug database content to understand visitor vehicle data structure
"""

def debug_database_content():
    """Check what's actually in the database"""
    
    script = '''
import os
import sys
import django

# Django 설정
sys.path.append('/home/kyb9852/vehicle-management-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from visitors.models import VisitorReservation
from vehicles.models import VisitorVehicle
from datetime import date, timedelta

User = get_user_model()

print("🔍 데이터베이스 콘텐츠 디버깅")
print("=" * 60)

# 1. 사용자 정보 확인
try:
    user = User.objects.get(username='newtest1754832743')
    print(f"✅ 사용자 정보:")
    print(f"   👤 사용자: {user.username}")
    print(f"   🏢 아파트: {user.apartment}")
    print(f"   📱 사용자 타입: {user.user_type}")
    print(f"   🏠 동호수: {getattr(user, 'dong', 'N/A')}동 {getattr(user, 'ho', 'N/A')}호")
except User.DoesNotExist:
    print("❌ 사용자를 찾을 수 없습니다")
    sys.exit(1)

print()

# 2. VisitorReservation 모델 확인
print("📋 VisitorReservation 데이터:")
today = date.today()
print(f"   📅 오늘 날짜: {today}")

# 전체 VisitorReservation 확인
all_reservations = VisitorReservation.objects.all()
print(f"   📊 전체 VisitorReservation: {all_reservations.count()}개")

if all_reservations.exists():
    print("   📋 최근 5개 예약:")
    for i, reservation in enumerate(all_reservations.order_by('-created_at')[:5], 1):
        print(f"      {i}. 차량: {reservation.vehicle_number}")
        print(f"         방문자: {reservation.visitor_name}")
        print(f"         날짜: {reservation.visit_date}")
        print(f"         승인: {reservation.is_approved}")
        print(f"         등록자: {reservation.resident.username}")
        print(f"         등록자 아파트: {reservation.resident.apartment}")
        print()

# 3. 특정 필터링 조건으로 확인
print("🔍 API 필터링 조건별 확인:")

# API 조건 1: 오늘 이후 + 승인된 것 + 아파트별
if user.apartment:
    apartment_today = VisitorReservation.objects.filter(
        resident__apartment=user.apartment,
        visit_date__gte=today,
        is_approved=True
    )
    print(f"   🏢 아파트별 (오늘 이후, 승인): {apartment_today.count()}개")
    
    # 전체 기간으로 확인
    apartment_all = VisitorReservation.objects.filter(
        resident__apartment=user.apartment,
        is_approved=True
    )
    print(f"   🏢 아파트별 (전체 기간, 승인): {apartment_all.count()}개")
    
    # 승인 상관없이
    apartment_all_any = VisitorReservation.objects.filter(
        resident__apartment=user.apartment
    )
    print(f"   🏢 아파트별 (전체 기간, 승인무관): {apartment_all_any.count()}개")

# API 조건 2: 본인이 등록한 것만
user_reservations = VisitorReservation.objects.filter(
    resident=user,
    visit_date__gte=today,
    is_approved=True
)
print(f"   👤 본인 등록 (오늘 이후, 승인): {user_reservations.count()}개")

user_all = VisitorReservation.objects.filter(resident=user)
print(f"   👤 본인 등록 (전체 기간, 승인무관): {user_all.count()}개")

# 4. VisitorVehicle 모델도 확인 (혹시 다른 모델 사용?)
print()
print("🚗 VisitorVehicle 데이터:")
try:
    visitor_vehicles = VisitorVehicle.objects.all()
    print(f"   📊 전체 VisitorVehicle: {visitor_vehicles.count()}개")
    
    if visitor_vehicles.exists():
        for i, vehicle in enumerate(visitor_vehicles[:3], 1):
            print(f"      {i}. 차량: {vehicle.vehicle_number}")
            print(f"         등록자: {vehicle.registered_by.username}")
            print(f"         아파트: {vehicle.apartment}")
            print(f"         활성: {vehicle.is_active}")
except Exception as e:
    print(f"   ❌ VisitorVehicle 오류: {e}")

# 5. 대시보드 카운터 로직 재현
print()
print("📊 대시보드 카운터 로직 재현:")
try:
    if user.apartment:
        # 대시보드 카운터와 동일한 로직
        all_apartment_visitors = VisitorReservation.objects.filter(
            resident__apartment=user.apartment,
            visit_date__gte=today,
            is_approved=True
        )
        print(f"   🎯 대시보드 카운터 로직: {all_apartment_visitors.count()}개")
        
        # 날짜 조건 없이
        all_apartment_any_date = VisitorReservation.objects.filter(
            resident__apartment=user.apartment,
            is_approved=True
        )
        print(f"   🎯 대시보드 (날짜무관): {all_apartment_any_date.count()}개")
        
except Exception as e:
    print(f"   ❌ 대시보드 로직 오류: {e}")

print()
print("✅ 디버깅 완료")
'''
    
    with open('/home/kyb9852/vehicle-management-system/debug_db.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✅ 데이터베이스 디버깅 스크립트 생성 완료")

if __name__ == "__main__":
    debug_database_content()