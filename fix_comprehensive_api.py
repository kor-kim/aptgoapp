#!/usr/bin/env python3
"""
Comprehensive API 수정 스크립트
Resident 모델에서 차량 데이터를 가져오도록 수정
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
sys.path.append('/home/kyb9852/vehicle-management-system')
django.setup()

from accounts.models import User, Apartment
from vehicles.models import Resident, VisitorVehicle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

def create_fixed_comprehensive_api():
    """수정된 comprehensive API 뷰 함수 생성"""
    
    api_code = '''@csrf_exempt
@api_auth_required
def comprehensive_vehicle_data_api(request):
    """포괄적인 차량 데이터 새로고침 API - FIXED VERSION"""
    if request.method != 'GET':
        return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=405)
    
    # 권한 체크: 메인아이디 또는 관리단 권한 부아이디만 접근 가능
    user = request.user
    
    # 메인아이디는 무조건 권한 허용
    if user.user_type == 'main_account':
        pass
    # 부아이디는 is_manager가 True인 경우만 허용
    elif user.user_type == 'sub_account':
        if not (hasattr(user, 'is_manager') and user.is_manager):
            return JsonResponse({
                'success': False, 
                'error': '관리단 권한이 필요합니다. 일반 부아이디는 차량 데이터 새로고침 권한이 없습니다.'
            }, status=403)
    else:
        return JsonResponse({
            'success': False,
            'error': '차량 데이터 새로고침 권한이 없습니다.'
        }, status=403)
    
    try:
        # 데이터 범위 결정
        if user.user_type == 'main_account':
            # 메인아이디: 해당 아파트의 모든 데이터
            apartment = user.apartment
            if not apartment:
                return JsonResponse({'error': '아파트 정보가 없습니다.'}, status=400)
            
            # 1. 차량 데이터 - RESIDENT 모델에서 가져오기 (수정된 부분)
            residents_with_vehicles = Resident.objects.filter(
                apartment=apartment
            ).select_related('apartment')
            
            # 2. 입주민 정보 (메인아이디가 생성한 모든 부아이디)
            residents_queryset = User.objects.filter(
                parent_account=user,
                user_type='sub_account',
                is_active=True
            )
            
            # 3. 방문차량 정보 (해당 아파트의 모든 방문차량)
            visitor_vehicles_queryset = VisitorVehicle.objects.filter(
                apartment=apartment,
                is_active=True
            ).select_related('registered_by')
            
            # 4. 부아이디 정보 (메인아이디가 생성한 모든 부아이디)
            sub_accounts_queryset = User.objects.filter(
                parent_account=user,
                user_type='sub_account',
                is_active=True
            )
            
        else:
            # 부아이디 (관리단 권한): 자신이 속한 아파트의 데이터만
            if not user.parent_account or not user.parent_account.apartment:
                return JsonResponse({'error': '상위 계정 또는 아파트 정보가 없습니다.'}, status=400)
            
            apartment = user.parent_account.apartment
            
            # 1. 차량 데이터 - RESIDENT 모델에서 가져오기 (수정된 부분)
            residents_with_vehicles = Resident.objects.filter(
                apartment=apartment
            ).select_related('apartment')
            
            # 2. 입주민 정보 (같은 메인아이디 하위의 모든 부아이디)
            residents_queryset = User.objects.filter(
                parent_account=user.parent_account,
                user_type='sub_account',
                is_active=True
            )
            
            # 3. 방문차량 정보 (같은 아파트의 모든 방문차량)
            visitor_vehicles_queryset = VisitorVehicle.objects.filter(
                apartment=apartment,
                is_active=True
            ).select_related('registered_by')
            
            # 4. 부아이디 정보 (같은 메인아이디 하위의 모든 부아이디)
            sub_accounts_queryset = User.objects.filter(
                parent_account=user.parent_account,
                user_type='sub_account',
                is_active=True
            )
        
        # 데이터 직렬화 - RESIDENT 모델을 차량 데이터로 변환 (수정된 부분)
        vehicles_data = []
        for resident in residents_with_vehicles:
            vehicles_data.append({
                'id': resident.id,
                'plateNumber': resident.vehicle_number,
                'vehicleType': 'resident',  # Resident 모델은 모두 입주민 차량
                'ownerName': resident.username,
                'ownerPhone': resident.phone or '',
                'dong': resident.dong or '',
                'ho': resident.ho or '',
                'registeredDate': resident.created_at.isoformat() if hasattr(resident, 'created_at') else timezone.now().isoformat(),
                'isActive': True  # Resident 모델의 데이터는 모두 활성으로 간주
            })
        
        residents_data = []
        for resident in residents_queryset:
            residents_data.append({
                'id': resident.id,
                'username': resident.username,
                'phone': resident.phone or '',
                'dong': resident.dong or '',
                'ho': resident.ho or '',
                'user_type': resident.user_type,
                'parent_account': resident.parent_account.username if resident.parent_account else ''
            })
        
        visitor_vehicles_data = []
        for visitor in visitor_vehicles_queryset:
            visitor_vehicles_data.append({
                'id': visitor.id,
                'plateNumber': visitor.vehicle_number,
                'ownerName': visitor.contact,  # 연락처를 ownerName으로 매핑
                'contactNumber': visitor.contact,
                'visitDate': visitor.created_at.strftime('%Y-%m-%d'),
                'registeredBy': visitor.registered_by.username if visitor.registered_by else '',
                'dong': visitor.visiting_dong,
                'ho': visitor.visiting_ho,
                'isActive': visitor.is_active
            })
        
        sub_accounts_data = []
        for sub_account in sub_accounts_queryset:
            sub_accounts_data.append({
                'id': sub_account.id,
                'username': sub_account.username,
                'user_type': sub_account.user_type,
                'is_manager': sub_account.is_manager if hasattr(sub_account, 'is_manager') else False,
                'parent_account': sub_account.parent_account.username if sub_account.parent_account else '',
                'dong': sub_account.dong or '',
                'ho': sub_account.ho or ''
            })
        
        response_data = {
            'vehicles': vehicles_data,
            'residents': residents_data,
            'visitorVehicles': visitor_vehicles_data,
            'subAccounts': sub_accounts_data,
            'success': True,
            'message': f'총 {len(vehicles_data)}대 차량, {len(residents_data)}명 입주민, {len(visitor_vehicles_data)}대 방문차량 데이터를 조회했습니다.',
            'lastUpdated': int(timezone.now().timestamp() * 1000)  # 밀리초 단위
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=500)
'''
    
    return api_code

def backup_and_replace_views():
    """기존 views.py 백업하고 수정된 함수로 교체"""
    
    import shutil
    from datetime import datetime
    
    views_path = '/home/kyb9852/vehicle-management-system/vehicles/views.py'
    backup_path = f'/home/kyb9852/vehicle-management-system/vehicles/views.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # 백업 생성
    shutil.copy2(views_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # 기존 파일 읽기
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # comprehensive_vehicle_data_api 함수 찾기
    start_marker = "def comprehensive_vehicle_data_api(request):"
    end_marker = "            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'"
    
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("❌ comprehensive_vehicle_data_api 함수를 찾을 수 없습니다.")
        return False
    
    # 함수 끝 찾기 (다음 함수 시작 또는 파일 끝)
    lines = content[start_pos:].split('\n')
    end_line = 0
    
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('def ') or line.startswith('@') and not line.strip().startswith('    '):
            end_line = i
            break
    
    if end_line == 0:
        end_line = len(lines)
    
    # 교체할 함수 범위 계산
    before_function = content[:start_pos]
    after_function_start = start_pos + len('\n'.join(lines[:end_line]))
    after_function = content[after_function_start:]
    
    # 새로운 함수로 교체
    new_function = create_fixed_comprehensive_api()
    new_content = before_function + new_function + after_function
    
    # 파일 쓰기
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ comprehensive_vehicle_data_api 함수 교체 완료")
    return True

def test_resident_data():
    """Resident 모델 데이터 확인"""
    print("\n🔍 Resident 모델 데이터 확인:")
    
    try:
        # 전체 Resident 개수
        total_residents = Resident.objects.count()
        print(f"   - 전체 Resident 수: {total_residents}개")
        
        # 샘플 데이터
        sample_residents = Resident.objects.all()[:5]
        print(f"   - 샘플 데이터:")
        for i, resident in enumerate(sample_residents, 1):
            print(f"     {i}. 차량번호: {resident.vehicle_number}")
            print(f"        위치: {resident.dong}동 {resident.ho}호")
            print(f"        소유자: {resident.username}")
            print(f"        연락처: {resident.phone}")
            print(f"        아파트: {resident.apartment}")
            print()
    
    except Exception as e:
        print(f"   ❌ 오류: {e}")

def main():
    print("=" * 60)
    print("🔧 Comprehensive API 수정 스크립트")
    print("=" * 60)
    
    # 1. 현재 데이터 상태 확인
    test_resident_data()
    
    # 2. API 함수 교체
    print("\n🔄 API 함수 수정 중...")
    if backup_and_replace_views():
        print("✅ API 수정 완료")
    else:
        print("❌ API 수정 실패")
        return
    
    print("\n" + "=" * 60)
    print("🏁 수정 완료 - Django 서버 재시작 필요")
    print("=" * 60)

if __name__ == "__main__":
    main()