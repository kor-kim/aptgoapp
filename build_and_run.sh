#!/bin/bash

# Android 앱 빌드 및 실행 스크립트

echo "==================================="
echo "Android 앱 빌드 및 실행"
echo "==================================="

# 프로젝트 디렉토리로 이동
cd /Users/dragonship/파이썬/aptgoapp

# Gradle Wrapper 실행 권한 부여
chmod +x gradlew

echo ""
echo "1. 프로젝트 정리..."
./gradlew clean

echo ""
echo "2. 프로젝트 빌드..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 빌드 성공!"
    echo ""
    echo "3. APK 파일 위치:"
    echo "   app/build/outputs/apk/debug/app-debug.apk"
    
    echo ""
    echo "4. 에뮬레이터 또는 기기에 설치하려면:"
    echo "   ./gradlew installDebug"
    
    echo ""
    echo "5. 설치 후 실행하려면:"
    echo "   adb shell am start -n org.aptgo.vehiclemanager/.MainActivity"
else
    echo ""
    echo "❌ 빌드 실패!"
    echo "에러 메시지를 확인하세요."
fi
