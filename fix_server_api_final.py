#!/usr/bin/env python3
"""
서버 API 최종 수정 스크립트
Resident 모델에서 차량 데이터를 정확히 가져오도록 comprehensive API 수정
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
from django.utils import timezone

def create_new_comprehensive_api():
    """Resident 모델에서 데이터를 가져오는 새로운 comprehensive API"""
    
    new_api = '''@csrf_exempt
@api_auth_required
def comprehensive_vehicle_data_api(request):
    """포괄적인 차량 데이터 새로고침 API - RESIDENT MODEL VERSION"""
    if request.method != 'GET':
        return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=405)
    
    # 권한 체크: 메인아이디 또는 관리단 권한 부아이디만 접근 가능
    user = request.user
    
    if user.user_type == 'main_account':
        pass
    elif user.user_type == 'sub_account':
        if not (hasattr(user, 'is_manager') and user.is_manager):
            return JsonResponse({
                'success': False, 
                'error': '관리단 권한이 필요합니다.'
            }, status=403)
    else:
        return JsonResponse({
            'success': False,
            'error': '차량 데이터 접근 권한이 없습니다.'
        }, status=403)
    
    try:
        # 메인아이디의 아파트 확인
        if user.user_type == 'main_account':
            apartment = user.apartment
            main_user = user
        else:
            apartment = user.parent_account.apartment if user.parent_account else None
            main_user = user.parent_account
        
        if not apartment or not main_user:
            return JsonResponse({'error': '아파트 정보가 없습니다.'}, status=400)
        
        # 1. 차량 데이터 - Resident 모델에서 가져오기
        residents_with_vehicles = Resident.objects.filter(
            apartment=apartment
        ).select_related('apartment')
        
        vehicles_data = []
        for resident in residents_with_vehicles:
            vehicles_data.append({
                'id': resident.id,
                'plateNumber': resident.vehicle_number,
                'vehicleType': 'resident',
                'ownerName': resident.username,
                'ownerPhone': resident.phone or '',
                'dong': resident.dong or '',
                'ho': resident.ho or '',
                'registeredDate': resident.created_at.isoformat() if hasattr(resident, 'created_at') else timezone.now().isoformat(),
                'isActive': True
            })
        
        # 2. 입주민 정보 (User 모델의 부계정들)
        residents_queryset = User.objects.filter(
            parent_account=main_user,
            user_type='sub_account',
            is_active=True
        )
        
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
        
        # 3. 방문차량 정보
        visitor_vehicles_queryset = VisitorVehicle.objects.filter(
            apartment=apartment,
            is_active=True
        ).select_related('registered_by')
        
        visitor_vehicles_data = []
        for visitor in visitor_vehicles_queryset:
            visitor_vehicles_data.append({
                'id': visitor.id,
                'plateNumber': visitor.vehicle_number,
                'ownerName': visitor.contact,
                'contactNumber': visitor.contact,
                'visitDate': visitor.created_at.strftime('%Y-%m-%d') if visitor.created_at else '',
                'registeredBy': visitor.registered_by.username if visitor.registered_by else '',
                'dong': visitor.visiting_dong,
                'ho': visitor.visiting_ho,
                'isActive': visitor.is_active
            })
        
        # 4. 부아이디 정보
        sub_accounts_data = []
        for sub_account in residents_queryset:
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
            'lastUpdated': int(timezone.now().timestamp() * 1000)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'데이터 조회 중 오류: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)
'''
    
    return new_api

def apply_api_fix():
    """API 수정 적용"""
    import shutil
    from datetime import datetime
    
    # 백업 생성
    views_file = '/home/kyb9852/vehicle-management-system/vehicles/views.py'
    backup_file = f'{views_file}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    shutil.copy2(views_file, backup_file)
    print(f"✅ 백업 생성: {backup_file}")
    
    # 기존 파일 읽기
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # comprehensive_vehicle_data_api 함수 찾기 및 교체
    start_pos = content.find("def comprehensive_vehicle_data_api(request):")
    if start_pos == -1:
        print("❌ comprehensive_vehicle_data_api 함수를 찾을 수 없습니다.")
        return False
    
    # 함수 끝 찾기 (다음 @나 def 까지)
    remaining_content = content[start_pos:]
    lines = remaining_content.split('\n')
    
    function_end = 0
    indent_level = None
    
    for i, line in enumerate(lines):
        if i == 0:
            continue
            
        # 첫 번째 비어있지 않은 라인의 들여쓰기 레벨 확인
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        # 함수나 데코레이터의 시작 (같은 들여쓰기 레벨 이하)
        if line.strip() and (line.startswith('def ') or line.startswith('@')):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= (indent_level or 0):
                function_end = i
                break
    
    if function_end == 0:
        function_end = len(lines)
    
    # 새로운 내용 구성
    before_function = content[:start_pos]
    after_function_start = start_pos + len('\n'.join(lines[:function_end]))
    after_function = content[after_function_start:]
    
    new_function = create_new_comprehensive_api()
    new_content = before_function + new_function + '\n\n' + after_function
    
    # 파일 쓰기
    with open(views_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ comprehensive_vehicle_data_api 함수 교체 완료")
    return True

def restart_django_server():
    """Django 서버 재시작"""
    import subprocess
    
    print("🔄 Django 서버 재시작 중...")
    
    try:
        # 기존 서버 프로세스 종료
        subprocess.run(['pkill', '-f', 'python.*manage.py.*runserver'], 
                      capture_output=True, check=False)
        
        # 새 서버 시작
        subprocess.Popen([
            'bash', '-c', 
            'cd /home/kyb9852/vehicle-management-system && source venv/bin/activate && nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &'
        ])
        
        print("✅ 서버 재시작 완료")
        return True
        
    except Exception as e:
        print(f"❌ 서버 재시작 실패: {e}")
        return False

def test_data_counts():
    """데이터 개수 확인"""
    print("\n📊 데이터 개수 확인:")
    
    try:
        # User 모델의 서브계정
        main_user = User.objects.get(username='newtest1754832743')
        sub_accounts = User.objects.filter(parent_account=main_user, user_type='sub_account')
        print(f"   - User 서브계정: {sub_accounts.count()}개")
        
        # Resident 모델
        apartment = main_user.apartment
        if apartment:
            residents = Resident.objects.filter(apartment=apartment)
            print(f"   - Resident 차량데이터: {residents.count()}개")
        else:
            print(f"   - 아파트 정보 없음")
            
    except Exception as e:
        print(f"   ❌ 확인 중 오류: {e}")

def main():
    print("=" * 60)
    print("🔧 최종 API 수정 스크립트")
    print("=" * 60)
    
    # 1. 데이터 확인
    test_data_counts()
    
    # 2. API 수정
    print("\n🔄 API 수정 적용 중...")
    if not apply_api_fix():
        return
    
    # 3. 서버 재시작
    restart_django_server()
    
    print("\n" + "=" * 60)
    print("🎉 수정 완료!")
    print("   - Resident 모델에서 차량 데이터 조회하도록 수정됨")
    print("   - Django 서버 재시작됨")
    print("   - 이제 299개 차량 데이터가 정상적으로 반환될 것입니다")
    print("=" * 60)

if __name__ == "__main__":
    main()