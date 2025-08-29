package org.aptgo.vehiclemanager.models

data class User(
    val id: Int,
    val username: String,
    val user_type: String, // main_account, sub_account 등
    val is_manager: Boolean = false,
    val dong: String? = null,
    val ho: String? = null,
    val phone: String? = null,
    val parent_account: String? = null,
    val communityId: String? = null,
    val communityName: String? = null
) {
    // 기존 코드와의 호환성을 위한 getter
    val userId: String get() = id.toString()
    val userRole: String get() = user_type
    
    // 권한 시스템을 위한 기본 권한 (서버에서 따로 오지 않으므로 user_type 기반으로 생성)
    val permissions: List<String> get() {
        return when (user_type) {
            "main_account" -> listOf("scan_vehicles", "view_reports", "manage_accounts", "refresh_vehicle_data")
            "sub_account" -> if (is_manager) listOf("scan_vehicles", "refresh_vehicle_data") else listOf("scan_vehicles")
            else -> emptyList()
        }
    }
    
    // 차량 데이터 새로고침 권한 체크
    fun canRefreshVehicleData(): Boolean {
        android.util.Log.d("User", "canRefreshVehicleData - user_type: $user_type, is_manager: $is_manager")
        return user_type == "main_account" || (user_type == "sub_account" && is_manager)
    }
}