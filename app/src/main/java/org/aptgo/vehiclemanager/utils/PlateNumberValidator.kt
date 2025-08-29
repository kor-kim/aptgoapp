package org.aptgo.vehiclemanager.utils

object PlateNumberValidator {
    
    // Korean plate number patterns
    private val PLATE_PATTERNS = listOf(
        Regex("\\d{2,3}[가-힣]\\d{4}"), // 12가3456 or 123가4567
        Regex("[가-힣]{2}\\d{2}[가-힣]\\d{4}"), // 서울12가3456
    )
    
    private val KOREAN_CHARS = listOf(
        "가", "나", "다", "라", "마", "거", "너", "더", "러", "머",
        "버", "서", "어", "저", "고", "노", "도", "로", "모", "보",
        "소", "오", "조", "구", "누", "두", "루", "무", "부", "수",
        "우", "주", "아", "바", "사", "자", "허", "배", "호", "하"
    )
    
    fun extractPlateNumber(text: String): String? {
        val cleanText = text.replace("\\s".toRegex(), "")
            .replace("O", "0") // Common OCR mistake
            .replace("o", "0")
            .replace("I", "1")
            .replace("l", "1")
        
        // Try to find a matching pattern
        for (pattern in PLATE_PATTERNS) {
            val match = pattern.find(cleanText)
            if (match != null) {
                return match.value
            }
        }
        
        // Try to extract partial matches
        val possiblePlate = extractPossiblePlate(cleanText)
        if (isValidPlateFormat(possiblePlate)) {
            return possiblePlate
        }
        
        return null
    }
    
    private fun extractPossiblePlate(text: String): String {
        val result = StringBuilder()
        var hasNumber = false
        var hasKorean = false
        
        for (char in text) {
            when {
                char.isDigit() -> {
                    result.append(char)
                    hasNumber = true
                }
                char in '가'..'힣' && KOREAN_CHARS.any { it[0] == char } -> {
                    result.append(char)
                    hasKorean = true
                }
            }
            
            // Stop if we have a reasonable length
            if (result.length >= 7 && hasNumber && hasKorean) {
                break
            }
        }
        
        return result.toString()
    }
    
    fun isValidPlateFormat(plateNumber: String): Boolean {
        if (plateNumber.length < 6 || plateNumber.length > 9) {
            return false
        }
        
        return PLATE_PATTERNS.any { it.matches(plateNumber) }
    }
    
    fun calculateConfidence(text: String): Float {
        val extractedPlate = extractPlateNumber(text)
        if (extractedPlate == null) {
            return 0f
        }
        
        // Simple confidence calculation based on format matching
        return when {
            PLATE_PATTERNS[0].matches(extractedPlate) -> 0.95f
            PLATE_PATTERNS[1].matches(extractedPlate) -> 0.90f
            else -> 0.70f
        }
    }
    
    fun formatPlateNumber(plateNumber: String): String {
        // Format plate number for display
        return plateNumber.uppercase()
    }
}