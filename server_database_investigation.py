#!/usr/bin/env python3
"""
Server-side database investigation script
Run this on the server to investigate visitor vehicle data
"""

def investigate_database():
    """Investigation script to run on Django server"""
    
    script_content = '''#!/usr/bin/env python3
import os
import sys
import django
from datetime import date

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from visitors.models import VisitorReservation
from datetime import date, timedelta

User = get_user_model()

print("🔍 서버 데이터베이스 조사 시작")
print("=" * 70)

# 1. 테스트 사용자 확인
try:
    user = User.objects.get(username='newtest1754832743')
    print(f"✅ 사용자 발견:")
    print(f"   👤 사용자명: {user.username}")
    print(f"   🏢 아파트: {user.apartment}")
    print(f"   📱 사용자 타입: {user.user_type}")
    print(f"   ✅ 승인됨: {user.is_approved}")
    print(f"   💎 프리미엄: {user.is_premium}")
    
    if hasattr(user, 'dong') and hasattr(user, 'ho'):
        print(f"   🏠 동호수: {user.dong}동 {user.ho}호")
    
except User.DoesNotExist:
    print("❌ 테스트 사용자를 찾을 수 없습니다")
    sys.exit(1)

print()

# 2. 전체 VisitorReservation 현황
all_reservations = VisitorReservation.objects.all()
print(f"📊 전체 VisitorReservation 레코드: {all_reservations.count()}개")

if all_reservations.exists():
    print("   📋 최근 등록된 방문차량 5개:")
    for i, reservation in enumerate(all_reservations.order_by('-created_at')[:5], 1):
        print(f"      {i}. 차량번호: {reservation.vehicle_number}")
        print(f"         방문자: {reservation.visitor_name}")  
        print(f"         방문날짜: {reservation.visit_date}")
        print(f"         등록자: {reservation.resident.username}")
        print(f"         등록자 아파트: {reservation.resident.apartment}")
        print(f"         승인상태: {reservation.is_approved}")
        if hasattr(reservation, 'visit_datetime'):
            print(f"         방문시간: {reservation.visit_datetime}")
        print()

# 3. 대시보드 카운터 로직 재현
today = date.today()
print(f"📅 오늘 날짜: {today}")

if user.apartment:
    # 대시보드와 동일한 필터링 로직
    dashboard_logic = VisitorReservation.objects.filter(
        resident__apartment=user.apartment,
        visit_date__gte=today,
        is_approved=True
    )
    print(f"🎯 대시보드 로직 결과: {dashboard_logic.count()}개")
    
    if dashboard_logic.exists():
        print("   ✅ 대시보드 로직으로 발견된 차량들:")
        for reservation in dashboard_logic.order_by('-created_at'):
            print(f"      - {reservation.vehicle_number} ({reservation.visitor_name})")
            print(f"        등록자: {reservation.resident.username}")
            print(f"        아파트: {reservation.resident.apartment}")
    else:
        print("   ❌ 대시보드 로직으로 차량을 찾을 수 없음")
    
    # 날짜 조건 없이 확인
    dashboard_no_date = VisitorReservation.objects.filter(
        resident__apartment=user.apartment,
        is_approved=True
    )
    print(f"📊 날짜 조건 없는 대시보드 로직: {dashboard_no_date.count()}개")
    
    # 승인 조건 없이 확인  
    apartment_all = VisitorReservation.objects.filter(
        resident__apartment=user.apartment
    )
    print(f"📊 아파트별 전체 (승인무관): {apartment_all.count()}개")

# 4. API 로직 재현
if user.user_type == 'main_account':
    if user.apartment:
        api_logic = VisitorReservation.objects.filter(
            resident__apartment=user.apartment,
            visit_date__gte=today,
            is_approved=True
        ).select_related('resident')
    else:
        api_logic = VisitorReservation.objects.filter(
            resident=user,
            visit_date__gte=today,
            is_approved=True
        ).select_related('resident')
else:
    api_logic = VisitorReservation.objects.filter(
        resident=user,
        visit_date__gte=today,
        is_approved=True
    ).select_related('resident')

print(f"🛠️ API 로직 결과: {api_logic.count()}개")

if api_logic.exists():
    print("   ✅ API 로직으로 발견된 차량들:")
    for reservation in api_logic.order_by('-created_at'):
        print(f"      - {reservation.vehicle_number} ({reservation.visitor_name})")
        print(f"        등록자: {reservation.resident.username}")
        print(f"        아파트: {reservation.resident.apartment}")
        print(f"        방문날짜: {reservation.visit_date}")
else:
    print("   ❌ API 로직으로 차량을 찾을 수 없음")

# 5. 디버깅: 단계별 필터링 결과
print("\\n🔍 단계별 디버깅:")

# 5.1 아파트별 모든 레코드
if user.apartment:
    step1 = VisitorReservation.objects.filter(resident__apartment=user.apartment)
    print(f"   1단계 - 아파트별 필터: {step1.count()}개")
    
    # 5.2 오늘 이후 필터 추가
    step2 = step1.filter(visit_date__gte=today)
    print(f"   2단계 - 오늘 이후 추가: {step2.count()}개")
    
    # 5.3 승인된 것만 필터 추가  
    step3 = step2.filter(is_approved=True)
    print(f"   3단계 - 승인된 것만: {step3.count()}개")
    
    if step1.exists():
        print("\\n   📋 아파트별 모든 레코드:")
        for reservation in step1.order_by('-created_at'):
            print(f"      - {reservation.vehicle_number}")
            print(f"        방문날짜: {reservation.visit_date} (오늘: {today})")
            print(f"        승인상태: {reservation.is_approved}")
            print(f"        등록자: {reservation.resident.username}")

print("\\n✅ 데이터베이스 조사 완료")
'''
    
    # Write the investigation script
    with open('/tmp/db_investigate.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 서버 데이터베이스 조사 스크립트 생성 완료")
    print("📝 스크립트 위치: /tmp/db_investigate.py")
    print("🚀 서버에서 실행 방법:")
    print("   1. cd /home/kyb9852/vehicle-management-system")  
    print("   2. source venv/bin/activate")
    print("   3. python /tmp/db_investigate.py > investigation_result.txt")

if __name__ == "__main__":
    investigate_database()