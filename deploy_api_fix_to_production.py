#!/usr/bin/env python3
"""
Deploy the API model fix to production server
Changes visitor_vehicles_api from VisitorVehicle to VisitorReservation model
"""

def create_production_deployment_script():
    """Create deployment script for production server"""
    
    # The corrected API function for production deployment
    corrected_api_code = '''@login_required
def visitor_vehicles_api(request):
    """실시간 방문차량 목록 조회 API - VisitorReservation 사용으로 수정"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
    
    try:
        from django.utils import timezone
        from datetime import date
        
        today = date.today()
        
        # 사용자 유형에 따른 방문차량 조회 (VisitorReservation 사용)
        if request.user.user_type == 'sub_account':
            # 부아이디: 자신이 등록한 방문차량만 조회
            reservations = VisitorReservation.objects.filter(
                resident=request.user,
                visit_date__gte=today,
                is_approved=True
            ).select_related('resident').order_by('-created_at')
        elif request.user.user_type in ['admin', 'super_admin', 'main_account']:
            # 메인아이디: 해당 아파트의 모든 방문차량 조회 (대시보드와 동일 로직)
            apartment = request.user.apartment
            if apartment:
                reservations = VisitorReservation.objects.filter(
                    resident__apartment=apartment,
                    visit_date__gte=today,
                    is_approved=True
                ).select_related('resident').order_by('-created_at')
            else:
                reservations = VisitorReservation.objects.none()
        else:
            return JsonResponse({'error': '권한이 없습니다.'}, status=403)
        
        # JSON 형태로 데이터 변환
        visitor_vehicles = []
        for reservation in reservations:
            # 한국 시간으로 변환
            visit_datetime_kr = None
            if hasattr(reservation, 'visit_datetime') and reservation.visit_datetime:
                visit_datetime_kr = timezone.localtime(reservation.visit_datetime)
            created_at_kr = timezone.localtime(reservation.created_at)
            
            visitor_vehicles.append({
                'id': reservation.id,
                'vehicle_number': reservation.vehicle_number,
                'visitor_name': reservation.visitor_name,
                'contact': reservation.visitor_phone,
                'visit_date': reservation.visit_date.strftime('%Y-%m-%d') if reservation.visit_date else '',
                'visit_time': reservation.visit_time.strftime('%H:%M') if reservation.visit_time else '',
                'visit_datetime': visit_datetime_kr.strftime('%Y-%m-%d %H:%M') if visit_datetime_kr else '',
                'purpose': reservation.purpose,
                'registered_by': reservation.resident.username if reservation.resident else '',
                'registered_by_apartment': reservation.resident.apartment if reservation.resident else '',
                'created_at': created_at_kr.strftime('%Y-%m-%d %H:%M'),
                'is_approved': reservation.is_approved
            })
        
        return JsonResponse({
            'visitor_vehicles': visitor_vehicles,
            'success': True,
            'count': len(visitor_vehicles)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'오류가 발생했습니다: {str(e)}',
            'success': False
        }, status=500)'''

    # Create the deployment script content
    deployment_script = f'''#!/usr/bin/env python3
"""
Production deployment script for visitor_vehicles_api fix
Run this script on the production server
"""

import re

def deploy_api_fix():
    """Deploy the API model fix on production server"""
    
    print("🚀 프로덕션 서버 API 수정 배포 시작")
    print("=" * 60)
    
    # Read the current accounts/views.py file
    try:
        with open('/home/kyb9852/vehicle-management-system/accounts/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ accounts/views.py 파일 읽기 성공")
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {{e}}")
        return False
    
    # Check if VisitorReservation import exists
    if 'from visitors.models import VisitorReservation' not in content:
        print("⚠️ VisitorReservation import가 없어서 추가합니다")
        
        # Find the import section and add VisitorReservation import
        import_pattern = r'(try:\\s*\\n\\s*from vehicles\\.models import.*?\\nexcept ImportError:.*?\\n)'
        import_replacement = r'\\1\\ntry:\\n    from visitors.models import VisitorReservation\\nexcept ImportError:\\n    VisitorReservation = None\\n'
        
        content = re.sub(import_pattern, import_replacement, content, flags=re.DOTALL)
        print("✅ VisitorReservation import 추가")
    else:
        print("✅ VisitorReservation import 이미 존재")
    
    # Pattern to match the current visitor_vehicles_api function  
    pattern = r'@login_required\\s*\\ndef visitor_vehicles_api\\(request\\):.*?except Exception as e:.*?status=500\\)'
    
    # Replace with corrected function
    corrected_function = """{corrected_api_code}"""
    
    new_content = re.sub(pattern, corrected_function, content, flags=re.DOTALL)
    
    if new_content != content:
        # Create backup first
        import shutil
        from datetime import datetime
        backup_name = f'/home/kyb9852/vehicle-management-system/accounts/views.py.backup_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}'
        shutil.copy('/home/kyb9852/vehicle-management-system/accounts/views.py', backup_name)
        print(f"✅ 백업 생성: {{backup_name}}")
        
        # Write the updated content
        with open('/home/kyb9852/vehicle-management-system/accounts/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ visitor_vehicles_api 함수 수정 완료!")
        print("   🔄 VisitorVehicle → VisitorReservation 변경")
        print("   🎯 대시보드 카운터와 동일한 데이터 소스 사용")
        print("   📊 응답 형식: visitor_vehicles 배열 유지")
        
        return True
    else:
        print("❌ 패턴 매칭 실패 - 이미 수정되었거나 수동 수정 필요")
        return False

def restart_django_server():
    """Restart Django server after deployment"""
    import subprocess
    
    print("\\n🔄 Django 서버 재시작")
    print("-" * 40)
    
    try:
        # Kill existing Django processes
        subprocess.run(['pkill', '-f', 'python manage.py runserver'], check=False)
        print("✅ 기존 Django 프로세스 종료")
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Start Django server in background
        subprocess.Popen([
            'bash', '-c', 
            'cd /home/kyb9852/vehicle-management-system && source venv/bin/activate && nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &'
        ])
        print("✅ Django 서버 재시작 완료")
        print("📍 서버 주소: http://34.57.99.61:8000/")
        print("📍 도메인: https://aptgo.org")
        
        return True
    except Exception as e:
        print(f"❌ 서버 재시작 실패: {{e}}")
        return False

if __name__ == "__main__":
    print("🔧 프로덕션 API 수정 배포 스크립트")
    print("📅 배포 시간: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    print()
    
    # Deploy the fix
    deploy_success = deploy_api_fix()
    
    if deploy_success:
        print("\\n🎉 API 수정 배포 성공!")
        
        # Restart server
        restart_success = restart_django_server()
        
        if restart_success:
            print("\\n✅ 배포 및 재시작 완료!")
            print("🧪 테스트 방법:")
            print("   1. https://aptgo.org/login/ 접속")
            print("   2. newtest1754832743 / admin123 로그인")
            print("   3. 대시보드에서 '방문차량' 버튼 클릭")
            print("   4. 등록된 방문차량 목록 확인")
        else:
            print("\\n⚠️ 배포는 성공했지만 서버 재시작 실패")
            print("💡 수동으로 서버를 재시작해주세요")
    else:
        print("\\n❌ API 수정 배포 실패")
        print("💡 수동으로 수정이 필요할 수 있습니다")
'''
    
    # Write the deployment script
    with open('/tmp/deploy_production_api_fix.py', 'w', encoding='utf-8') as f:
        f.write(deployment_script)
    
    print("✅ 프로덕션 배포 스크립트 생성 완료!")
    print("📝 스크립트 위치: /tmp/deploy_production_api_fix.py")
    print()
    print("🚀 배포 방법:")
    print("1. 서버에 스크립트 복사:")
    print("   scp /tmp/deploy_production_api_fix.py kyb9852@34.57.99.61:/tmp/")
    print()
    print("2. 서버에서 스크립트 실행:")  
    print("   ssh kyb9852@34.57.99.61")
    print("   python3 /tmp/deploy_production_api_fix.py")
    print()
    print("3. 배포 후 테스트:")
    print("   https://aptgo.org/login/ → newtest1754832743/admin123 로그인")
    print("   대시보드 → '방문차량' 버튼 클릭 → 데이터 확인")

if __name__ == "__main__":
    create_production_deployment_script()