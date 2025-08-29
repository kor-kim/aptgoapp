# IntelliJ IDEA에서 Android 개발 설정

## 1. Android 플러그인 설치
1. IntelliJ IDEA → Preferences (⌘,)
2. Plugins 선택
3. "Android" 검색
4. Android 플러그인 설치
5. IDE 재시작

## 2. Android SDK 설정
1. File → Project Structure
2. Platform Settings → SDKs
3. "+" 버튼 → Android SDK 추가
4. Android SDK 경로 설정:
   - macOS: ~/Library/Android/sdk
   - 또는 Android Studio에서 사용하는 SDK 경로

## 3. 프로젝트 설정 변경
1. File → Project Structure
2. Project Settings → Modules
3. aptgoapp 모듈 선택
4. "+" → Android 선택
5. Android SDK 선택

## 4. Run Configuration 생성
1. Run → Edit Configurations
2. "+" → Android App
3. Module: app 선택
4. Deploy: Default APK
5. Launch: Default Activity

## 5. Gradle 동기화
1. View → Tool Windows → Gradle
2. Refresh 버튼 클릭
3. 동기화 완료 대기

## 주의사항:
- IntelliJ Community Edition에서는 Android 개발이 제한적
- Android Studio가 Android 개발에 최적화되어 있음
- 가능하면 Android Studio 사용 권장
