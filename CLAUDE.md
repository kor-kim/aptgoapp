# 🚗 AptGo Vehicle Manager - Android App Development Guide

## 📱 프로젝트 개요

**아파트 관리단을 위한 차량 번호판 인식 및 관리 안드로이드 앱**

- **프로젝트명**: AptGo Vehicle Manager  
- **서버 연동**: https://aptgo.org (Django 백엔드)
- **패키지명**: org.aptgo.vehiclemanager
- **언어**: Kotlin
- **최소 SDK**: 24 (Android 7.0)
- **타겟 SDK**: 34

## 🏗️ 아키텍처 구조

### Android 프로젝트 구조
```
aptgoapp/
├── app/
│   ├── build.gradle                 # 앱 레벨 빌드 설정
│   └── src/main/
│       ├── AndroidManifest.xml      # 앱 설정 및 권한
│       ├── java/org/aptgo/vehiclemanager/
│       │   ├── activities/          # 액티비티 (화면)
│       │   │   ├── LoginActivity.kt       # 로그인
│       │   │   ├── MainActivity.kt        # 메인 대시보드
│       │   │   ├── CameraScanActivity.kt  # 카메라 스캔
│       │   │   ├── ManualSearchActivity.kt # 수동 검색
│       │   │   └── VehicleDetailActivity.kt # 차량 상세
│       │   ├── database/            # Room 데이터베이스
│       │   │   ├── AppDatabase.kt         # DB 설정
│       │   │   ├── VehicleDao.kt          # 차량 DAO
│       │   │   └── ScanHistoryDao.kt      # 스캔 기록 DAO
│       │   ├── models/              # 데이터 모델
│       │   │   ├── Vehicle.kt             # 차량 엔티티
│       │   │   ├── User.kt                # 사용자 모델
│       │   │   └── ScanHistory.kt         # 스캔 기록
│       │   ├── network/             # 네트워크 레이어
│       │   │   ├── ApiService.kt          # API 인터페이스
│       │   │   └── NetworkModule.kt       # Retrofit 설정
│       │   └── utils/               # 유틸리티
│       │       ├── UserSession.kt         # 사용자 세션
│       │       ├── PreferenceManager.kt   # SharedPreferences
│       │       └── VehicleDataSync.kt     # 데이터 동기화
│       └── res/
│           ├── layout/              # XML 레이아웃 파일
│           ├── values/              # 문자열, 색상, 테마
│           └── drawable/            # 아이콘 및 이미지
├── build.gradle                     # 프로젝트 레벨 빌드 설정
├── settings.gradle                  # 프로젝트 설정
└── gradle/                          # Gradle wrapper
```

### 데이터 플로우
```
aptgo.org Django 서버
    ↓ API 통신 (Bearer Token 인증)
Android App
    ├── Network Layer (Retrofit + OkHttp)
    ├── Local Database (Room SQLite)
    ├── UI Layer (Activities + View Binding)
    └── Camera/OCR (CameraX + ML Kit)
```

## 🔧 개발 환경 설정

### 필수 요구사항
- **Android Studio**: Arctic Fox (2020.3.1) 이상
- **JDK**: OpenJDK 11
- **Android SDK**: API 34
- **Kotlin**: 1.9.22
- **Gradle**: 8.2.2

### 프로젝트 설정
```bash
# 프로젝트 디렉토리 이동
cd /Users/dragonship/파이썬/aptgoapp

# Gradle 빌드
./gradlew build

# 디버그 APK 빌드
./gradlew assembleDebug

# 빠른 빌드 스크립트
./quick_build.sh

# 빌드 및 설치 스크립트  
./build_and_run.sh
```

### 의존성 관리 (app/build.gradle)
```gradle
// 핵심 라이브러리
androidx.core:core-ktx:1.12.0
androidx.appcompat:appcompat:1.6.1
com.google.android.material:material:1.10.0

// CameraX (카메라 기능)
androidx.camera:camera-*:1.3.0

// ML Kit OCR (번호판 인식)
com.google.mlkit:text-recognition:16.0.0
com.google.mlkit:text-recognition-korean:16.0.0

// Room Database (로컬 저장소)
androidx.room:room-*:2.6.0

// Retrofit (API 통신)
com.squareup.retrofit2:retrofit:2.9.0
com.squareup.retrofit2:converter-gson:2.9.0
```

## 🔐 인증 및 보안

### 로그인 플로우
1. **LoginActivity**: aptgo.org 계정 입력
2. **API 호출**: POST /api/login
3. **토큰 저장**: Bearer Token (Encrypted SharedPreferences)
4. **사용자 세션**: UserSession.user에 정보 저장
5. **메인 화면**: MainActivity로 이동

### API 인증
```kotlin
// Authorization Header 사용
@GET("api/vehicles")
suspend fun getVehicles(
    @Header("Authorization") token: String,
    @Query("community_id") communityId: String?
): Response<VehicleListResponse>
```

### 보안 기능
- **Encrypted SharedPreferences**: 토큰 및 사용자 정보 암호화 저장
- **HTTPS 통신**: 모든 API 호출 암호화
- **토큰 자동 갱신**: Refresh Token 메커니즘
- **앱 권한 관리**: 카메라, 네트워크, 저장소

## 📡 서버 통신

### API 엔드포인트 (aptgo.org)
```kotlin
interface ApiService {
    @POST("api/login")                    // 로그인
    @GET("api/vehicles")                  // 차량 목록 조회
    @POST("api/reports/scan")             // 스캔 결과 리포트
    @POST("api/reports/daily")            // 일일 사용 리포트
    @GET("api/user/profile")              // 사용자 프로필
    @POST("api/refresh-token")            // 토큰 갱신
}
```

### 데이터 동기화
```kotlin
// MainActivity.kt:syncVehicleData()
val response = NetworkModule.apiService.getVehicles("Bearer $token", communityId)
if (response.isSuccessful) {
    val vehicles = response.body()!!.vehicles
    database.vehicleDao().deleteAllVehicles()
    database.vehicleDao().insertVehicles(vehicles)
}
```

## 📷 카메라 및 OCR

### CameraX 구현
- **실시간 미리보기**: 번호판 스캔 오버레이
- **자동 포커스**: 번호판 인식 최적화
- **이미지 캡처**: 스캔 결과 저장

### ML Kit OCR
- **한국어 번호판 특화**: Korean Text Recognition
- **실시간 인식**: 카메라 프레임별 처리
- **신뢰도 필터링**: 인식 정확도 임계값 설정

### 스캔 플로우
1. **카메라 권한 확인**
2. **CameraScanActivity 실행**
3. **실시간 OCR 처리**
4. **번호판 패턴 검증** (PlateNumberValidator)
5. **로컬 DB 검색** (등록 차량 여부)
6. **결과 표시** (VehicleDetailActivity)

## 💾 로컬 데이터 관리

### Room Database 구조
```kotlin
@Database(
    entities = [Vehicle::class, ScanHistory::class, User::class],
    version = 1
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun vehicleDao(): VehicleDao
    abstract fun scanHistoryDao(): ScanHistoryDao
}
```

### 주요 엔티티
- **Vehicle**: 차량 정보 (번호판, 소유자, 동호수 등)
- **ScanHistory**: 스캔 기록 (시간, 타입, 결과)
- **User**: 사용자 정보 (관리단 정보)

### 데이터 동기화 전략
- **서버 우선**: 로그인 시 서버 데이터로 로컬 DB 업데이트
- **오프라인 모드**: 네트워크 오류 시 로컬 DB 기반 동작
- **주기적 동기화**: 설정에 따른 자동 동기화

## 🎨 UI/UX 설계

### Material Design 3
- **테마**: Theme.AptgoVehicleManager
- **색상 팔레트**: 아파트 관리 시스템 브랜딩
- **다크 모드**: 시스템 설정 따라 자동 전환

### 주요 화면 구성
1. **LoginActivity**: 로그인 폼
2. **MainActivity**: 대시보드 (통계, 바로가기)
3. **CameraScanActivity**: 실시간 번호판 스캔
4. **ManualSearchActivity**: 키패드 기반 수동 검색
5. **VehicleDetailActivity**: 차량 상세 정보
6. **HistoryActivity**: 스캔 기록 조회
7. **SettingsActivity**: 앱 설정

### 한국어 특화 UI
- **커스텀 키패드**: KoreanPlateKeypadView
- **번호판 형식**: 한국 번호판 패턴 최적화
- **한글 OCR**: 한국어 문자 인식 지원

## 🧪 테스팅 및 디버깅

### 테스트 계정
```
서버: https://aptgo.org
관리자: super_admin / admin123#
일반 계정: 메인 계정에서 서브 계정 생성 후 사용
```

### 디버깅 도구
- **로그캣 필터**: `org.aptgo.vehiclemanager`
- **네트워크 로깅**: OkHttp Interceptor
- **데이터베이스 검사**: Room Inspector

### 일반적인 문제 해결

#### 1. 카메라 권한 거부
```kotlin
// 권한 요청 처리 (PermissionX 사용)
PermissionX.init(this)
    .permissions(Manifest.permission.CAMERA)
    .request { allGranted, _, _ ->
        if (allGranted) initCamera()
        else showPermissionDeniedDialog()
    }
```

#### 2. OCR 인식률 저하
- **조명 환경**: 충분한 조명 필요
- **카메라 각도**: 번호판과 수직으로 정렬
- **신뢰도 임계값**: 설정에서 조정 가능

#### 3. 네트워크 연결 오류
```kotlin
// 오프라인 모드 지원
try {
    // API 호출
} catch (e: Exception) {
    // 로컬 DB로 fallback
    Toast.makeText(this, "오프라인 모드", Toast.LENGTH_SHORT).show()
}
```

#### 4. 토큰 만료 처리
```kotlin
// 자동 토큰 갱신
if (response.code() == 401) {
    val refreshed = refreshToken()
    if (refreshed) retry() else logout()
}
```

## 📊 성능 최적화

### 메모리 관리
- **이미지 처리**: Glide를 통한 메모리 효율적 로딩
- **카메라 자원**: 액티비티 생명주기에 따른 해제
- **데이터베이스**: 적절한 인덱싱 및 쿼리 최적화

### 배터리 최적화
- **백그라운드 제한**: 필요시에만 네트워크 요청
- **카메라 사용**: 사용 후 즉시 자원 해제
- **위치 서비스**: 필요한 경우에만 활성화

## 🚀 빌드 및 배포

### 개발 빌드
```bash
# 디버그 APK 생성
./gradlew assembleDebug

# 설치 및 실행
./gradlew installDebug
adb shell am start -n org.aptgo.vehiclemanager/.activities.LoginActivity
```

### 릴리즈 빌드
```bash
# 릴리즈 APK 생성 (keystore 필요)
./gradlew assembleRelease

# APK 위치: app/build/outputs/apk/release/
```

### ProGuard 설정
```pro
# Retrofit
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }

# Room
-keep class androidx.room.** { *; }

# ML Kit
-keep class com.google.mlkit.** { *; }
```

## 🔗 서버 연동 세부사항

### Django 백엔드 API 규격
```python
# aptgo.org Django 서버의 예상 API 엔드포인트
GET  /api/vehicles/?community_id={id}      # 차량 목록
POST /api/login/                           # 로그인
POST /api/reports/scan/                    # 스캔 리포트
GET  /api/user/profile/                    # 사용자 정보
```

### 데이터 모델 매핑
```kotlin
// Android Vehicle Model → Django Vehicle Model
data class Vehicle(
    val vehicleId: String,        // Django: vehicle_id
    val plateNumber: String,      // Django: plate_number  
    val ownerName: String,        // Django: owner_name
    val unitNumber: String,       // Django: unit_number
    val communityId: String?      // Django: community_id
)
```

## 📋 개발 워크플로우

### 새 기능 개발
1. **기능 설계**: UI/UX 목업 작성
2. **모델 정의**: Kotlin 데이터 클래스 생성
3. **API 연동**: ApiService 인터페이스 확장
4. **로컬 저장**: Room DAO 및 Entity 수정
5. **UI 구현**: Activity/Fragment 작성
6. **테스트**: 단위 테스트 및 UI 테스트
7. **배포**: APK 빌드 및 배포

### 버그 수정 절차
1. **재현**: 로그캣으로 오류 확인
2. **분석**: 코드 디버깅 및 원인 파악  
3. **수정**: 코드 수정 및 검증
4. **테스트**: 회귀 테스트 실행
5. **배포**: 패치 버전 배포

### 코드 스타일
- **Kotlin Style Guide**: Android Kotlin 스타일 가이드 준수
- **네이밍**: 한국어 주석, 영어 변수명
- **아키텍처**: MVVM 패턴 권장

## 🎯 Claude Code 개발 가이드

### Android 개발 명령어
```bash
# 프로젝트 빌드
./gradlew build

# 클린 빌드
./gradlew clean build

# 디버그 설치
./gradlew installDebug

# 로그 확인
adb logcat -s "AptgoVehicleManager"
```

### 주요 개발 파일
- **MainActivity.kt**:77 - syncVehicleData() 메서드 (서버 동기화)
- **ApiService.kt**:15 - API 인터페이스 정의
- **Vehicle.kt**:12 - 차량 데이터 모델
- **AndroidManifest.xml**:31 - LoginActivity가 LAUNCHER

### 자주 사용하는 패턴
```kotlin
// API 호출 패턴
lifecycleScope.launch {
    try {
        val response = NetworkModule.apiService.getVehicles("Bearer $token")
        if (response.isSuccessful) {
            // 성공 처리
        }
    } catch (e: Exception) {
        // 오류 처리
    }
}

// Room DB 패턴
database.vehicleDao().insertVehicles(vehicles)
val count = database.scanHistoryDao().getTodayScansCount()
```

---

## 📞 개발 지원

### 서버 정보
- **Production**: https://aptgo.org
- **API Base**: https://aptgo.org/api/
- **관리자**: super_admin / admin123#

### 개발 환경
- **로컬 빌드**: /Users/dragonship/파이썬/aptgoapp
- **Android Studio**: 프로젝트 최적화 완료
- **빌드 도구**: Gradle 8.2.2

---

*최종 업데이트: 2025-08-26 - Android 차량 관리 앱 개발 가이드*