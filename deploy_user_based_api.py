#!/usr/bin/env python3
"""
Deploy User-based comprehensive API to server
Replace Resident model query with User model vehicle_number query
"""

import os
import sys
import subprocess
from datetime import datetime

def deploy_api_fix():
    """Deploy the User-based API fix to server"""
    
    user_based_api = '''@csrf_exempt
@api_auth_required
def comprehensive_vehicle_data_api(request):
    """User 모델 vehicle_number 기반 포괄적인 차량 데이터 새로고침 API"""
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
        
        # User 모델에서 vehicle_number가 있는 서브 계정들 조회 (핵심 수정사항)
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
        
        # 입주민 정보 (User 모델의 부계정들)
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
        
        # 방문차량 정보 (기존 로직 유지)
        visitor_vehicles_queryset = VisitorVehicle.objects.filter(
            apartment=main_user.apartment,
            is_active=True
        ).select_related('registered_by') if main_user.apartment else VisitorVehicle.objects.none()
        
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
        
        # 부아이디 정보
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
            'error': f'오류: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)'''

    # Save the new API function to a file
    print("📝 User-based API 함수를 서버에 배포 중...")
    
    with open('/tmp/new_api_function.py', 'w', encoding='utf-8') as f:
        f.write(user_based_api)
    
    print("✅ API 함수 파일 생성 완료")
    return True

def restart_django_server():
    """Django 서버 재시작"""
    print("🔄 Django 서버 재시작 중...")
    
    try:
        # 서버 재시작 명령
        result = subprocess.run([
            'gcloud', 'compute', 'ssh', 'kyb9852@instance-20250723-044453',
            '--zone=us-central1-c',
            '--command=cd /home/kyb9852/vehicle-management-system && pkill -f "python.*manage.py.*runserver" && source venv/bin/activate && nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &'
        ], capture_output=True, text=True)
        
        print("✅ 서버 재시작 명령 실행됨")
        print(f"출력: {result.stdout}")
        if result.stderr:
            print(f"경고: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ 서버 재시작 실패: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 User-based API 배포 스크립트")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. API 함수 생성
    if not deploy_api_fix():
        print("❌ API 함수 생성 실패")
        return
    
    # 2. 서버 재시작 (수동으로 API 교체 후)
    print("\n📋 다음 단계:")
    print("1. 서버에 SSH 접속")
    print("2. views.py 파일에서 comprehensive_vehicle_data_api 함수 교체")
    print("3. Django 서버 재시작")
    print("4. API 응답 테스트")
    
    print("\n" + "=" * 60)
    print("✅ 준비 완료 - 수동 배포 필요")
    print("=" * 60)

if __name__ == "__main__":
    main()