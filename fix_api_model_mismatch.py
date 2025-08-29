#!/usr/bin/env python3
"""
Fix API model mismatch - use VisitorReservation instead of VisitorVehicle
The dashboard counts VisitorReservation but API queries VisitorVehicle
"""

def fix_api_model_mismatch():
    """Fix the visitor_vehicles_api to use VisitorReservation model like the dashboard"""
    
    # The corrected API function using VisitorReservation
    corrected_api = '''@login_required
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
    
    # Read the current file
    with open('/Users/dragonship/파이썬/ANPR/accounts/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the current visitor_vehicles_api function
    import re
    pattern = r'@login_required\s*\ndef visitor_vehicles_api\(request\):.*?except Exception as e:.*?status=500\)'
    
    # Replace with corrected function
    new_content = re.sub(pattern, corrected_api, content, flags=re.DOTALL)
    
    if new_content != content:
        # Write the updated content
        with open('/Users/dragonship/파이썬/ANPR/accounts/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ API 모델 불일치 수정 완료!")
        print("   🔄 VisitorVehicle → VisitorReservation 변경")
        print("   🎯 대시보드 카운터와 동일한 데이터 소스 사용")
        print("   📊 응답 형식: visitor_vehicles 배열 유지")
        return True
    else:
        print("❌ 패턴 매칭 실패 - 수동 수정 필요")
        return False

if __name__ == "__main__":
    print("🔧 API 모델 불일치 수정 중...")
    success = fix_api_model_mismatch()
    if success:
        print("🎉 수정 완료! 로컬 테스트 후 서버 배포 필요")
    else:
        print("❌ 자동 수정 실패")