# 아파트 차량 관리 시스템 - Android App

## 📱 프로젝트 개요
아파트 관리단을 위한 차량 번호판 인식 및 관리 앱입니다.

## 🔑 주요 기능
- **OCR 기반 자동 번호판 인식** (Google ML Kit 사용)
- **수동 번호판 입력** (커스텀 한국어 키패드)
- **등록 차량 조회** 및 **미등록 차량 처리**
- **스캔 기록 저장** 및 **통계 제공**
- **aptgo.org 서버 연동**

## 🛠 기술 스택
- **Language**: Kotlin
- **Database**: Room (SQLite)
- **Network**: Retrofit2 + OkHttp
- **Camera**: CameraX
- **OCR**: Google ML Kit Text Recognition (Korean)
- **UI**: Material Design Components
- **Security**: Encrypted SharedPreferences

## 📂 프로젝트 구조
```
app/
├── src/main/java/org/aptgo/vehiclemanager/
│   ├── activities/          # 액티비티 클래스들
│   ├── adapters/            # RecyclerView 어댑터
│   ├── database/            # Room DB 관련
│   ├── models/              # 데이터 모델
│   ├── network/             # API 서비스
│   ├── utils/               # 유틸리티 클래스
│   └── views/               # 커스텀 뷰
├── src/main/res/
│   ├── layout/              # XML 레이아웃
│   ├── values/              # 리소스 값
│   ├── drawable/            # 아이콘 및 드로어블
│   └── menu/                # 메뉴 정의
└── build.gradle
```

## 🚀 빌드 방법

### 1. 환경 설정
- Android Studio 최신 버전
- Android SDK 34 이상
- Kotlin 1.9.0 이상

### 2. 프로젝트 열기
```bash
# Android Studio에서 'aptgoapp' 폴더 열기
```

### 3. 의존성 설치
```bash
./gradlew build
```

### 4. 실행
- Android 기기 또는 에뮬레이터 연결
- Run 버튼 클릭 또는 `./gradlew installDebug`

## 📋 사용법

### 로그인
- aptgo.org 계정으로 로그인
- 관리단 계정이 필요합니다

### 차량 스캔
1. **카메라 스캔**: 메인 화면에서 "카메라 스캔" 선택
   - 번호판에 카메라를 향하면 자동 인식
   - 연속 스캔 / 단일 캡처 모드 지원
   
2. **수동 입력**: "수동 검색" 선택
   - 커스텀 키패드로 번호판 직접 입력
   - 부분 검색 및 와일드카드(*) 지원

### 결과 처리
- **등록 차량**: 소유자 정보 표시
- **미등록 차량**: 조치 옵션 제공
  - 스티커 발부
  - 사진 촬영
  - 메모 작성

## 🔧 설정 항목
- 데이터 동기화 주기
- OCR 신뢰도 임계값
- 자동 로그인 설정
- 알림 설정

## 📊 통계 기능
- 일일 스캔 통계
- 자동/수동 스캔 비율
- 번호판 인식률
- 등록 차량 수

## 🛡️ 보안 기능
- 암호화된 로그인 정보 저장
- HTTPS 통신
- 토큰 기반 인증
- 자동 토큰 갱신

## 🔄 서버 연동
- **Base URL**: https://aptgo.org/
- **인증**: Bearer Token
- **데이터 동기화**: 로그인 시 + 수동 새로고침
- **오프라인 모드**: 로컬 DB 기반 동작

## 🧪 테스트 계정
- **최고관리자**: super_admin / admin123#
- **관리단**: (메인 계정에서 생성)

## 📱 지원 기기
- **Android**: 7.0 (API 24) 이상
- **카메라**: 후면 카메라 필수
- **권한**: 카메라, 저장공간, 네트워크

## 🐛 알려진 이슈
- 저조도 환경에서 인식률 저하
- 오염된 번호판 인식 어려움
- 일부 특수 번호판 형식 미지원

## 📝 개발 계획
- [ ] 차량 사진 자동 촬영 기능
- [ ] 음성 입력 지원
- [ ] 다국어 지원 (영어, 중국어)
- [ ] 위반 차량 알림 시스템
- [ ] 통계 차트 개선

## 🤝 기여 방법
1. Fork 프로젝트
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📄 라이센스
이 프로젝트는 private repository입니다.

## 📞 문의사항
기술 지원: aptgo.org 관리자