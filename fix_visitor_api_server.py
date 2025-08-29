#!/usr/bin/env python3
"""
Fix visitor_vehicles_api function to use VisitorReservation instead of VisitorVehicle
"""

import re

def fix_visitor_vehicles_api():
    """Replace the visitor_vehicles_api function with the corrected version"""
    
    # Read current file
    with open('/home/kyb9852/vehicle-management-system/vehicles/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The corrected function code
    new_function = '''@login_required
def visitor_vehicles_api(request):
    """방문차량 목록 API (AJAX용)"""
    if request.user.user_type not in ['main_account', 'sub_account']:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)
    
    # 메인아이디는 해당 아파트의 모든 방문차량 조회 (VisitorReservation 사용)
    if request.user.user_type == 'main_account':
        # 메인아이디는 자신이 등록한 방문차량 조회
        vehicles = VisitorReservation.objects.filter(
            resident=request.user,
            is_approved=True
        ).select_related('resident')
    else:
        # 부아이디는 자신이 등록한 방문차량만 조회
        vehicles = VisitorReservation.objects.filter(
            resident=request.user,
            is_approved=True
        ).select_related('resident')
    
    vehicles_data = []
    for vehicle in vehicles.order_by('-created_at')[:10]:  # 최근 10개만
        # 삭제 권한 확인
        can_delete = (vehicle.resident == request.user)
        
        # 한국 시간으로 변환
        visit_datetime_kr = timezone.localtime(vehicle.visit_datetime) if vehicle.visit_datetime else None
        created_at_kr = timezone.localtime(vehicle.created_at)
        
        vehicles_data.append({
            'id': vehicle.id,
            'vehicle_number': vehicle.vehicle_number,
            'contact': vehicle.visitor_phone,
            'visitor_name': vehicle.visitor_name,
            'visit_date': vehicle.visit_date.strftime('%Y-%m-%d') if vehicle.visit_date else '',
            'visit_time': vehicle.visit_time.strftime('%H:%M') if vehicle.visit_time else '',
            'visit_datetime': visit_datetime_kr.strftime('%Y-%m-%d %H:%M') if visit_datetime_kr else '',
            'purpose': vehicle.purpose,
            'registered_by': vehicle.resident.username,
            'created_at': created_at_kr.strftime('%Y-%m-%d %H:%M'),
            'can_delete': can_delete
        })
    
    return JsonResponse({'vehicles': vehicles_data})'''
    
    # Pattern to match the entire visitor_vehicles_api function (including decorator)
    pattern = r'@login_required\s*\ndef visitor_vehicles_api\(request\):.*?return JsonResponse\({\'vehicles\': vehicles_data}\)'
    
    # Replace with new function
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content != content:
        # Write the updated content
        with open('/home/kyb9852/vehicle-management-system/vehicles/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully updated visitor_vehicles_api function")
        print("   Changed from VisitorVehicle to VisitorReservation model")
        return True
    else:
        print("❌ No changes made - pattern not found")
        return False

if __name__ == "__main__":
    print("🔧 Fixing visitor_vehicles_api function on server...")
    success = fix_visitor_vehicles_api()
    if success:
        print("🎉 Fix applied successfully!")
    else:
        print("❌ Fix failed to apply")