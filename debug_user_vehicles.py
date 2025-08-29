#!/usr/bin/env python3
"""
User 모델에서 차량 정보 직접 조회
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
sys.path.append('/home/kyb9852/vehicle-management-system')
django.setup()

from accounts.models import User
from vehicles.models import Resident

def check_user_vehicle_numbers():
    """User 모델에서 vehicle_number 필드 확인"""
    print("🔍 User 모델 vehicle_number 필드 확인:")
    
    try:
        # 메인 계정
        main_user = User.objects.get(username='newtest1754832743')
        print(f"   - 메인 계정: {main_user.username}")
        print(f"   - 아파트: {main_user.apartment}")
        
        # 서브 계정들
        sub_users = User.objects.filter(parent_account=main_user, user_type='sub_account')
        print(f"   - 전체 서브 계정 수: {sub_users.count()}개")
        
        # vehicle_number가 있는 서브 계정들
        users_with_vehicles = sub_users.exclude(vehicle_number__isnull=True).exclude(vehicle_number__exact='')
        print(f"   - vehicle_number가 있는 계정: {users_with_vehicles.count()}개")
        
        # 샘플 출력
        print(f"\n📋 샘플 차량 데이터 (처음 10개):")
        for i, user in enumerate(users_with_vehicles[:10], 1):
            print(f"   {i}. {user.username}")
            print(f"      차량번호: {user.vehicle_number or 'N/A'}")
            print(f"      위치: {user.dong or 'N/A'}동 {user.ho or 'N/A'}호")  
            print(f"      연락처: {user.phone or 'N/A'}")
            print()
            
        return users_with_vehicles
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def check_resident_vs_user():
    """Resident 모델 vs User 모델 비교"""
    print("\n🔍 Resident vs User 모델 비교:")
    
    try:
        main_user = User.objects.get(username='newtest1754832743')
        
        # Resident 모델
        if main_user.apartment:
            residents = Resident.objects.filter(apartment=main_user.apartment)
            print(f"   - Resident 테이블: {residents.count()}개")
            
            if residents.exists():
                sample = residents.first()
                print(f"   - Resident 샘플: {sample.vehicle_number} ({sample.username})")
        else:
            residents = Resident.objects.all()
            print(f"   - 전체 Resident 테이블: {residents.count()}개")
        
        # User 모델
        users_with_vehicles = User.objects.filter(
            parent_account=main_user, 
            user_type='sub_account'
        ).exclude(vehicle_number__isnull=True).exclude(vehicle_number__exact='')
        
        print(f"   - User vehicle_number: {users_with_vehicles.count()}개")
        
        if users_with_vehicles.exists():
            sample = users_with_vehicles.first()
            print(f"   - User 샘플: {sample.vehicle_number} ({sample.username})")
            
    except Exception as e:
        print(f"❌ 오류: {e}")

def create_user_based_api():
    """User 모델 기반의 API 수정"""
    
    api_code = '''@csrf_exempt
@api_auth_required
def comprehensive_vehicle_data_api(request):
    """User 모델 vehicle_number 기반 API"""
    if request.method != 'GET':
        return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=405)
    
    user = request.user
    
    if user.user_type == 'main_account':
        pass
    elif user.user_type == 'sub_account':
        if not (hasattr(user, 'is_manager') and user.is_manager):
            return JsonResponse({'success': False, 'error': '권한 없음'}, status=403)
    else:
        return JsonResponse({'success': False, 'error': '권한 없음'}, status=403)
    
    try:
        if user.user_type == 'main_account':
            main_user = user
        else:
            main_user = user.parent_account
        
        if not main_user:
            return JsonResponse({'error': '메인 계정 정보 없음'}, status=400)
        
        # User 모델에서 vehicle_number가 있는 서브 계정들 조회
        sub_users_with_vehicles = User.objects.filter(
            parent_account=main_user,
            user_type='sub_account',
            is_active=True
        ).exclude(vehicle_number__isnull=True).exclude(vehicle_number__exact='')
        
        vehicles_data = []
        for sub_user in sub_users_with_vehicles:
            vehicles_data.append({
                'id': sub_user.id,
                'plateNumber': sub_user.vehicle_number,
                'vehicleType': 'resident',
                'ownerName': sub_user.username,
                'ownerPhone': sub_user.phone or '',
                'dong': sub_user.dong or '',
                'ho': sub_user.ho or '',
                'registeredDate': sub_user.date_joined.isoformat(),
                'isActive': sub_user.is_active
            })
        
        # 입주민 정보
        residents_data = []
        all_sub_users = User.objects.filter(
            parent_account=main_user,
            user_type='sub_account',
            is_active=True
        )
        
        for resident in all_sub_users:
            residents_data.append({
                'id': resident.id,
                'username': resident.username,
                'phone': resident.phone or '',
                'dong': resident.dong or '',
                'ho': resident.ho or '',
                'user_type': resident.user_type,
                'parent_account': resident.parent_account.username if resident.parent_account else ''
            })
        
        response_data = {
            'vehicles': vehicles_data,
            'residents': residents_data,
            'visitorVehicles': [],
            'subAccounts': residents_data,
            'success': True,
            'message': f'총 {len(vehicles_data)}대 차량, {len(residents_data)}명 입주민, 0대 방문차량 데이터를 조회했습니다.',
            'lastUpdated': int(timezone.now().timestamp() * 1000)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'오류: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)
'''
    
    return api_code

def main():
    print("=" * 60)
    print("🔍 User 모델 차량 데이터 디버깅")
    print("=" * 60)
    
    # User 모델에서 vehicle_number 확인
    users_with_vehicles = check_user_vehicle_numbers()
    
    # Resident vs User 비교
    check_resident_vs_user()
    
    if users_with_vehicles and users_with_vehicles.count() > 0:
        print(f"\n✅ User 모델에 {users_with_vehicles.count()}개 차량 데이터 발견!")
        
        # User 기반 API 코드 생성
        print("\n📝 User 모델 기반 API 코드 생성:")
        api_code = create_user_based_api()
        
        # 파일 저장
        with open('/home/kyb9852/vehicle-management-system/user_based_api.py', 'w', encoding='utf-8') as f:
            f.write(api_code)
        print("✅ user_based_api.py 파일 저장됨")
        
    else:
        print("\n❌ User 모델에서도 차량 데이터를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()