#!/usr/bin/env python3
"""
Fix visitor_vehicles_api to match dashboard logic
Dashboard shows ALL apartment visitors, API should do the same
"""

import re

def fix_visitor_api_logic():
    """Fix the visitor_vehicles_api to match dashboard counting logic"""
    
    # Read current file
    with open('/home/kyb9852/vehicle-management-system/vehicles/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The corrected API function that matches dashboard logic
    new_function = '''@login_required
def visitor_vehicles_api(request):
    """방문차량 목록 API (AJAX용) - 대시보드 카운터 로직과 동일하게 수정"""
    if request.user.user_type not in ['main_account', 'sub_account']:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)
    
    from datetime import date
    today = date.today()
    
    # 메인아이디는 해당 아파트의 모든 방문차량 조회 (대시보드와 동일 로직)
    if request.user.user_type == 'main_account':
        if request.user.apartment:
            # 해당 아파트의 모든 방문차량 (오늘 이후, 승인된 것)
            vehicles = VisitorReservation.objects.filter(
                resident__apartment=request.user.apartment,
                visit_date__gte=today,
                is_approved=True
            ).select_related('resident')
        else:
            # 아파트 정보가 없으면 본인이 등록한 것만
            vehicles = VisitorReservation.objects.filter(
                resident=request.user,
                visit_date__gte=today,
                is_approved=True
            ).select_related('resident')
    else:
        # 부아이디는 자신이 등록한 방문차량만 조회
        vehicles = VisitorReservation.objects.filter(
            resident=request.user,
            visit_date__gte=today,
            is_approved=True
        ).select_related('resident')
    
    vehicles_data = []
    for vehicle in vehicles.order_by('-created_at')[:20]:  # 최근 20개
        # 삭제 권한 확인: 메인아이디는 아파트 내 모든 차량, 부아이디는 본인 것만
        if request.user.user_type == 'main_account' and request.user.apartment:
            can_delete = (vehicle.resident.apartment == request.user.apartment)
        else:
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
    
    # Pattern to match the entire visitor_vehicles_api function
    pattern = r'@login_required\s*\ndef visitor_vehicles_api\(request\):.*?return JsonResponse\({\'vehicles\': vehicles_data}\)'
    
    # Replace with new function
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content != content:
        # Write the updated content
        with open('/home/kyb9852/vehicle-management-system/vehicles/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully updated visitor_vehicles_api function")
        print("   🔄 Changed to match dashboard counting logic:")
        print("   📊 Main account: Shows ALL apartment visitor vehicles")
        print("   👤 Sub account: Shows only own visitor vehicles")
        return True
    else:
        print("❌ No changes made - pattern not found")
        return False

if __name__ == "__main__":
    print("🔧 Fixing visitor_vehicles_api logic to match dashboard counter...")
    success = fix_visitor_api_logic()
    if success:
        print("🎉 Logic fix applied successfully!")
    else:
        print("❌ Fix failed to apply")