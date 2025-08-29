#!/bin/bash
# 방문차량 API 수정사항 배포 스크립트

echo "🚀 방문차량 API 배포 시작"
echo "시간: $(date)"
echo "=========================="

# 1. 작업 디렉토리로 이동
cd /home/kyb9852/vehicle-management-system

# 2. 백업 생성
echo "📦 백업 생성 중..."
cp vehicles/views.py vehicles/views.py.backup_$(date +%Y%m%d_%H%M%S)
if [ $? -eq 0 ]; then
    echo "✅ 백업 완료"
else
    echo "❌ 백업 실패"
    exit 1
fi

# 3. Django 서비스 중지
echo "⏸️ Django 서비스 중지 중..."
sudo systemctl stop django
sleep 3
sudo systemctl status django --no-pager

# 4. views.py 수정
echo "🔧 views.py 파일 수정 중..."

# 첫 번째 수정: Line 520-524
sed -i 's/visitor_vehicles_queryset = VisitorVehicle.objects.filter(/from visitors.models import VisitorReservation\nvisitor_vehicles_queryset = VisitorReservation.objects.filter(/g' vehicles/views.py
sed -i 's/apartment=apartment,/resident__apartment=apartment,/g' vehicles/views.py
sed -i 's/is_active=True/is_approved=True/g' vehicles/views.py
sed -i 's/).select_related(.*registered_by.*/)/.select_related("resident")/g' vehicles/views.py

# 데이터 매핑 부분 수정
sed -i "s/'ownerName': visitor.contact,/'ownerName': visitor.visitor_name,/g" vehicles/views.py
sed -i "s/'contactNumber': visitor.contact,/'contactNumber': visitor.visitor_phone,/g" vehicles/views.py
sed -i "s/'visitDate': visitor.created_at.strftime('%Y-%m-%d'),/'visitDate': visitor.visit_date.strftime('%Y-%m-%d'),/g" vehicles/views.py
sed -i "s/'registeredBy': visitor.registered_by.username if visitor.registered_by else '',/'registeredBy': visitor.resident.username if visitor.resident else '',/g" vehicles/views.py
sed -i "s/'dong': visitor.visiting_dong,/'dong': visitor.resident.dong if visitor.resident else '',/g" vehicles/views.py
sed -i "s/'ho': visitor.visiting_ho,/'ho': visitor.resident.ho if visitor.resident else '',/g" vehicles/views.py
sed -i "s/'isActive': visitor.is_active/'isActive': visitor.is_approved/g" vehicles/views.py

echo "✅ 파일 수정 완료"

# 5. 방문차량 테스트 데이터 추가
echo "🚗 방문차량 테스트 데이터 추가 중..."
python3 manage.py shell -c "
from django.contrib.auth import get_user_model
from visitors.models import VisitorReservation
from datetime import date, time
User = get_user_model()

try:
    user = User.objects.get(username='newtest1754832743')
    print(f'사용자 찾음: {user.username}')
    
    # 기존 데이터 삭제
    existing_count = VisitorReservation.objects.filter(resident=user).count()
    if existing_count > 0:
        VisitorReservation.objects.filter(resident=user).delete()
        print(f'기존 {existing_count}개 데이터 삭제')
    
    # 6개 방문차량 추가
    test_data = [
        ('김방문1', '010-1111-2222', '12가1234', '친구 방문'),
        ('이방문2', '010-2222-3333', '34나5678', '택배 배송'),
        ('박방문3', '010-3333-4444', '56다9012', '수리 기사'),
        ('최방문4', '010-4444-5555', '78라3456', '가족 방문'),
        ('정방문5', '010-5555-6666', '90마7890', '업체 방문'),
        ('한방문6', '010-6666-7777', '12바1357', '친구 모임')
    ]
    
    created_count = 0
    for name, phone, plate, purpose in test_data:
        VisitorReservation.objects.create(
            resident=user,
            visitor_name=name,
            visitor_phone=phone,
            vehicle_number=plate,
            visit_date=date(2025, 8, 29),
            visit_time=time(14, 30),
            purpose=purpose,
            is_approved=True
        )
        created_count += 1
    
    print(f'{created_count}개 방문차량 데이터 추가 완료')
    
    # 검증
    total = VisitorReservation.objects.filter(resident=user, is_approved=True).count()
    print(f'최종 승인된 방문차량 수: {total}')
    
except Exception as e:
    print(f'오류 발생: {e}')
    import traceback
    traceback.print_exc()
"

if [ $? -eq 0 ]; then
    echo "✅ 테스트 데이터 추가 완료"
else
    echo "❌ 테스트 데이터 추가 실패"
fi

# 6. Django 서비스 시작
echo "▶️ Django 서비스 시작 중..."
sudo systemctl start django
sleep 5
sudo systemctl status django --no-pager

# 7. API 테스트
echo "🧪 API 테스트 중..."
sleep 3

# 로그인 테스트
echo "로그인 테스트..."
LOGIN_RESPONSE=$(curl -s -X POST https://aptgo.org/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newtest1754832743","password":"admin123"}')

echo "로그인 응답: $LOGIN_RESPONSE"

# 토큰 추출 시도
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', 'dummy-token'))" 2>/dev/null || echo "dummy-token")
echo "사용할 토큰: ${TOKEN:0:20}..."

# API 호출 테스트
echo "API 호출 테스트..."
API_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" https://aptgo.org/api/comprehensive/)
echo "API 응답 (처음 500자): ${API_RESPONSE:0:500}..."

# 방문차량 수 확인
VISITOR_COUNT=$(echo $API_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('visitorVehicles', [])))" 2>/dev/null || echo "0")
echo "방문차량 수: $VISITOR_COUNT"

if [ "$VISITOR_COUNT" = "6" ]; then
    echo "🎉 배포 성공! 방문차량 6개 확인됨"
else
    echo "⚠️ 방문차량 수가 예상과 다름: $VISITOR_COUNT (예상: 6)"
fi

echo "=========================="
echo "🏁 배포 완료: $(date)"
