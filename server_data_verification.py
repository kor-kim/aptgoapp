#!/usr/bin/env python3
"""
서버 데이터 검증 스크립트
실제 서버에 등록된 데이터 개수와 구조를 확인
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
sys.path.append('/home/kyb9852/vehicle-management-system')
django.setup()

from accounts.models import User
from vehicles.models import Vehicle
from django.db.models import Count, Q

def main():
    print("=" * 60)
    print("🔍 서버 데이터 검증 - 실제 데이터 개수 확인")
    print("=" * 60)
    
    # 메인 계정 확인
    try:
        main_user = User.objects.get(username='newtest1754832743')
        print(f"✅ 메인 계정 확인: {main_user.username}")
        print(f"   - User Type: {main_user.user_type}")
        print(f"   - Is Approved: {main_user.is_approved}")
        print(f"   - Is Premium: {main_user.is_premium}")
    except User.DoesNotExist:
        print("❌ 메인 계정 'newtest1754832743'을 찾을 수 없습니다.")
        return
    
    # 서브 계정 개수 확인
    sub_accounts = User.objects.filter(parent_account=main_user)
    print(f"\n📊 서브 계정 통계:")
    print(f"   - 전체 서브 계정 수: {sub_accounts.count()}개")
    
    # 활성 서브 계정
    active_subs = sub_accounts.filter(is_active=True)
    print(f"   - 활성 서브 계정 수: {active_subs.count()}개")
    
    # 차량 정보가 있는 서브 계정
    subs_with_vehicles = sub_accounts.filter(vehicles__isnull=False).distinct()
    print(f"   - 차량 등록된 서브 계정: {subs_with_vehicles.count()}개")
    
    # 전체 차량 수
    total_vehicles = Vehicle.objects.filter(owner__parent_account=main_user)
    print(f"\n🚗 차량 데이터 통계:")
    print(f"   - 전체 차량 수: {total_vehicles.count()}개")
    
    # 차량 타입별 통계
    vehicle_types = total_vehicles.values('vehicle_type').annotate(count=Count('id'))
    for vtype in vehicle_types:
        print(f"   - {vtype['vehicle_type']}: {vtype['count']}개")
    
    # 활성 차량
    active_vehicles = total_vehicles.filter(status='active')
    print(f"   - 활성 차량: {active_vehicles.count()}개")
    
    # 샘플 차량 데이터 출력 (처음 10개)
    print(f"\n🔍 샘플 차량 데이터 (처음 10개):")
    sample_vehicles = total_vehicles[:10]
    for i, vehicle in enumerate(sample_vehicles, 1):
        print(f"   {i}. 번호판: {vehicle.plate_number}")
        print(f"      소유자: {vehicle.owner.username}")
        print(f"      위치: {getattr(vehicle.owner, 'dong', 'N/A')}-{getattr(vehicle.owner, 'ho', 'N/A')}")
        print(f"      연락처: {getattr(vehicle.owner, 'phone', 'N/A')}")
        print(f"      차량타입: {vehicle.vehicle_type}")
        print(f"      상태: {vehicle.status}")
        print()
    
    # API 응답 형태로 데이터 구성해보기
    print("=" * 60)
    print("📡 API 응답 형태 데이터 구성 테스트")
    print("=" * 60)
    
    # ComprehensiveVehicleDataResponse 형태로 데이터 구성
    api_data = {
        'vehicles': [],
        'residents': [],
        'visitorVehicles': [],
        'subAccounts': [],
        'success': True,
        'message': 'Data retrieved successfully',
        'lastUpdated': 0
    }
    
    # 차량 정보
    for vehicle in total_vehicles:
        vehicle_info = {
            'id': vehicle.id,
            'plateNumber': vehicle.plate_number,
            'vehicleType': vehicle.vehicle_type,
            'ownerName': vehicle.owner.username,
            'ownerPhone': getattr(vehicle.owner, 'phone', ''),
            'dong': getattr(vehicle.owner, 'dong', ''),
            'ho': getattr(vehicle.owner, 'ho', ''),
            'registeredDate': vehicle.created_at.isoformat() if hasattr(vehicle, 'created_at') else '',
            'isActive': vehicle.status == 'active'
        }
        api_data['vehicles'].append(vehicle_info)
    
    # 서브 계정 정보
    for sub in sub_accounts:
        sub_info = {
            'id': sub.id,
            'username': sub.username,
            'user_type': sub.user_type,
            'is_manager': getattr(sub, 'is_manager', False),
            'parent_account': main_user.username,
            'dong': getattr(sub, 'dong', ''),
            'ho': getattr(sub, 'ho', '')
        }
        api_data['subAccounts'].append(sub_info)
    
    print(f"API 응답 데이터 구성 완료:")
    print(f"   - vehicles: {len(api_data['vehicles'])}개")
    print(f"   - subAccounts: {len(api_data['subAccounts'])}개")
    
    # JSON 크기 계산
    import json
    json_data = json.dumps(api_data, ensure_ascii=False)
    json_size = len(json_data.encode('utf-8'))
    print(f"   - JSON 데이터 크기: {json_size:,} bytes ({json_size/1024:.1f} KB)")
    
    if json_size > 1024 * 1024:  # 1MB 이상
        print("   ⚠️  경고: JSON 데이터가 1MB를 초과합니다. 네트워크 전송 시 문제 가능성 있음")
    
    return api_data

if __name__ == "__main__":
    result = main()