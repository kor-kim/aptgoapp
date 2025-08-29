package org.aptgo.vehiclemanager.network

import org.aptgo.vehiclemanager.models.Vehicle
import org.aptgo.vehiclemanager.models.User
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    @POST("api/login/")
    suspend fun login(
        @Body loginRequest: LoginRequest
    ): Response<LoginResponse>

    @GET("api/vehicles/")
    suspend fun getVehicles(
        @Header("Authorization") token: String,
        @Query("community_id") communityId: String? = null
    ): Response<VehicleListResponse>

    @GET("api/comprehensive/")
    suspend fun getComprehensiveVehicleData(
        @Header("Authorization") token: String
    ): Response<ComprehensiveVehicleDataResponse>

    @POST("api/reports/scan/")
    suspend fun submitScanReport(
        @Header("Authorization") token: String,
        @Body scanReport: ScanReport
    ): Response<ApiResponse>

    @POST("api/reports/daily/")
    suspend fun submitDailyReport(
        @Header("Authorization") token: String,
        @Body dailyReport: DailyReport
    ): Response<ApiResponse>

    @GET("api/user/profile/")
    suspend fun getUserProfile(
        @Header("Authorization") token: String
    ): Response<User>

    @POST("api/refresh-token/")
    suspend fun refreshToken(
        @Body refreshRequest: RefreshTokenRequest
    ): Response<LoginResponse>
    
    @POST("anpr-reports/api/receive/")
    suspend fun sendScanReport(
        @Body reportData: Map<String, Any>
    ): Response<ScanReportResponse>
}

// Request/Response models
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val token: String? = null, // 서버가 token으로 응답
    val refreshToken: String?,
    val user: User,
    val success: Boolean,
    val message: String?
) {
    // 기존 코드와 호환을 위한 accessToken 속성
    val accessToken: String? get() = token
}

data class VehicleListResponse(
    val vehicles: List<Vehicle>,
    val success: Boolean,
    val message: String?
)

data class ScanReport(
    val plateNumber: String,
    val scanType: String,
    val isRegistered: Boolean,
    val location: String?,
    val actionTaken: String?,
    val notes: String?,
    val photoUrl: String?,
    val timestamp: Long
)

data class DailyReport(
    val date: String,
    val totalScans: Int,
    val autoScans: Int,
    val manualSearches: Int,
    val registeredCount: Int,
    val violationCount: Int,
    val actionsTaken: List<String>,
    val recognitionAccuracy: Float,
    val scannerId: String
)

data class ApiResponse(
    val success: Boolean,
    val message: String?
)

data class RefreshTokenRequest(
    val refreshToken: String
)

// 포괄적인 차량 데이터 응답
data class ComprehensiveVehicleDataResponse(
    val vehicles: List<VehicleInfo>,
    val residents: List<ResidentInfo>,
    val visitorVehicles: List<VisitorVehicle>,
    val subAccounts: List<SubAccountInfo>,
    val success: Boolean,
    val message: String?,
    val lastUpdated: Long
)

// 차량 정보 (comprehensive API용)
data class VehicleInfo(
    val id: Int,
    val plateNumber: String,
    val vehicleType: String,
    val ownerName: String,
    val ownerPhone: String?,
    val dong: String?,
    val ho: String?,
    val registeredDate: String,
    val isActive: Boolean
)

// 입주민 정보
data class ResidentInfo(
    val id: Int,
    val username: String,
    val phone: String?,
    val dong: String?,
    val ho: String?,
    val user_type: String,
    val parent_account: String?
)

// 방문자 차량 정보
data class VisitorVehicle(
    val id: Int,
    val plateNumber: String,
    val ownerName: String?,
    val contactNumber: String?,
    val visitDate: String?,
    val registeredBy: String?, // 등록한 부아이디
    val dong: String?,
    val ho: String?,
    val isActive: Boolean
)

// 부아이디 정보
data class SubAccountInfo(
    val id: Int,
    val username: String,
    val user_type: String,
    val is_manager: Boolean,
    val parent_account: String,
    val dong: String?,
    val ho: String?
)

// ANPR 스캔 보고서 응답
data class ScanReportResponse(
    val success: Boolean,
    val message: String,
    val report_id: Int?
)