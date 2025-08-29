#!/bin/bash

# Android 앱 빠른 실행 스크립트

echo "Android 앱 빌드 시작..."

cd /Users/dragonship/파이썬/aptgoapp

# Gradle wrapper 확인
if [ ! -f "gradlew" ]; then
    echo "❌ gradlew 파일이 없습니다."
    echo "Android Studio에서 프로젝트를 한 번 열어주세요."
    exit 1
fi

# 실행 권한 부여
chmod +x gradlew

# 클린 빌드
./gradlew clean

# Debug APK 빌드
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo "✅ 빌드 성공!"
    echo ""
    echo "APK 위치: app/build/outputs/apk/debug/app-debug.apk"
    echo ""
    echo "다음 명령으로 설치:"
    echo "./gradlew installDebug"
else
    echo "❌ 빌드 실패"
fi
