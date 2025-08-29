package org.aptgo.vehiclemanager.utils

import android.content.Context
import android.util.Log
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.aptgo.vehiclemanager.database.AppDatabase
import org.aptgo.vehiclemanager.models.Vehicle
import org.aptgo.vehiclemanager.network.NetworkModule
import org.aptgo.vehiclemanager.network.VehicleInfo
import org.aptgo.vehiclemanager.network.VisitorVehicle
import org.aptgo.vehiclemanager.network.ComprehensiveVehicleDataResponse
import java.util.*
import kotlin.math.min
import kotlin.math.pow

class VehicleDataSync {
    companion object {
        private const val TAG = "VehicleDataSync"
        private const val MAX_RETRY_ATTEMPTS = 3
        private const val CHUNK_SIZE = 100 // Process vehicles in chunks for large datasets
        private const val INITIAL_RETRY_DELAY = 1000L // 1 second
        
        // Progress callback for UI updates
        interface SyncProgressCallback {
            fun onProgress(current: Int, total: Int, message: String)
        }
        
        suspend fun syncVehicleData(
            context: Context, 
            token: String, 
            progressCallback: SyncProgressCallback? = null
        ): SyncResult {
            return withContext(Dispatchers.IO) {
                
                // Step 1: Validate prerequisites
                if (!validateSyncPrerequisites(context, token)) {
                    return@withContext SyncResult(
                        success = false,
                        message = "동기화 전제조건 검증 실패: 네트워크 연결 또는 인증 정보를 확인해주세요"
                    )
                }
                
                progressCallback?.onProgress(0, 100, "동기화 준비 중...")
                
                // Step 2: Backup current data for rollback capability
                val database = AppDatabase.getDatabase(context)
                val backupVehicles = createDataBackup(database)
                
                progressCallback?.onProgress(10, 100, "데이터 백업 완료")
                
                // Step 3: Attempt sync with retry logic
                val syncResult = attemptSyncWithRetry(token, progressCallback)
                
                if (syncResult.success) {
                    // Step 4: Process and validate data in chunks
                    val processResult = processDataInChunks(
                        context, 
                        syncResult, 
                        progressCallback
                    )
                    
                    if (!processResult.success) {
                        // Rollback on processing failure
                        rollbackData(database, backupVehicles)
                        return@withContext processResult
                    }
                    
                    progressCallback?.onProgress(100, 100, "동기화 완료")
                    return@withContext processResult
                    
                } else {
                    // Network sync failed, restore backup if needed
                    progressCallback?.onProgress(100, 100, "동기화 실패")
                    return@withContext syncResult
                }
            }
        }
        
        private suspend fun validateSyncPrerequisites(context: Context, token: String): Boolean {
            return try {
                // Basic validation
                if (token.isBlank()) {
                    Log.e(TAG, "Token is blank")
                    return false
                }
                
                // Network connectivity check could be added here
                // For now, just validate basic requirements
                true
            } catch (e: Exception) {
                Log.e(TAG, "Prerequisites validation failed", e)
                false
            }
        }
        
        private suspend fun createDataBackup(database: AppDatabase): List<Vehicle> {
            return try {
                val vehicles = mutableListOf<Vehicle>()
                database.vehicleDao().getAllVehicles().collect { vehicleList ->
                    vehicles.addAll(vehicleList)
                }
                Log.d(TAG, "Created backup of ${vehicles.size} vehicles")
                vehicles
            } catch (e: Exception) {
                Log.e(TAG, "Failed to create backup", e)
                emptyList()
            }
        }
        
        private suspend fun attemptSyncWithRetry(
            token: String, 
            progressCallback: SyncProgressCallback?
        ): SyncResult {
            var lastException: Exception? = null
            
            repeat(MAX_RETRY_ATTEMPTS) { attempt ->
                try {
                    progressCallback?.onProgress(
                        20 + (attempt * 20), 
                        100, 
                        "서버에서 데이터 다운로드 중... (시도 ${attempt + 1}/$MAX_RETRY_ATTEMPTS)"
                    )
                    
                    Log.d(TAG, "Starting sync attempt ${attempt + 1} of $MAX_RETRY_ATTEMPTS")
                    Log.d(TAG, "Using token: $token")
                    
                    val response = NetworkModule.apiService.getComprehensiveVehicleData("Bearer $token")
                    
                    if (response.isSuccessful && response.body()?.success == true) {
                        val data = response.body()!!
                        
                        Log.d(TAG, "Received data - Vehicles: ${data.vehicles.size}, " +
                                "Residents: ${data.residents.size}, " +
                                "Visitor Vehicles: ${data.visitorVehicles.size}, " +
                                "Sub Accounts: ${data.subAccounts.size}")
                        
                        return SyncResult(
                            success = true,
                            message = "데이터 다운로드 성공",
                            vehicleCount = data.vehicles.size,
                            residentCount = data.residents.size,
                            visitorVehicleCount = data.visitorVehicles.size,
                            subAccountCount = data.subAccounts.size,
                            rawData = data
                        )
                    } else {
                        val errorMsg = response.body()?.message ?: "서버 응답 오류 (${response.code()})"
                        Log.e(TAG, "API call failed: $errorMsg")
                        Log.e(TAG, "Response code: ${response.code()}")
                        
                        // Don't retry for authentication errors (4xx)
                        if (response.code() in 400..499) {
                            return SyncResult(
                                success = false,
                                message = "인증 오류: $errorMsg"
                            )
                        }
                        
                        lastException = Exception("HTTP ${response.code()}: $errorMsg")
                    }
                    
                } catch (e: Exception) {
                    Log.e(TAG, "Sync attempt ${attempt + 1} failed", e)
                    lastException = e
                    
                    // Don't retry for certain exceptions
                    if (e is java.net.UnknownHostException || 
                        e is javax.net.ssl.SSLException) {
                        return SyncResult(
                            success = false,
                            message = "네트워크 연결 오류: ${e.message}"
                        )
                    }
                }
                
                // Exponential backoff for retry delay
                if (attempt < MAX_RETRY_ATTEMPTS - 1) {
                    val delay = INITIAL_RETRY_DELAY * 2.0.pow(attempt).toLong()
                    Log.d(TAG, "Waiting ${delay}ms before retry...")
                    delay(delay)
                }
            }
            
            // All attempts failed
            return SyncResult(
                success = false,
                message = "동기화 실패 (${MAX_RETRY_ATTEMPTS}회 시도): ${lastException?.message}"
            )
        }
        
        private suspend fun processDataInChunks(
            context: Context, 
            syncResult: SyncResult,
            progressCallback: SyncProgressCallback?
        ): SyncResult {
            return try {
                val rawData = syncResult.rawData ?: return SyncResult(
                    success = false,
                    message = "처리할 데이터가 없습니다"
                )
                
                val data = rawData as? ComprehensiveVehicleDataResponse ?: return SyncResult(
                    success = false,
                    message = "데이터 형식이 올바르지 않습니다"
                )
                
                val database = AppDatabase.getDatabase(context)
                val vehicleDao = database.vehicleDao()
                
                // Clear existing data
                vehicleDao.deleteAllVehicles()
                progressCallback?.onProgress(70, 100, "기존 데이터 정리 완료")
                
                val vehiclesToInsert = mutableListOf<Vehicle>()
                
                // Convert resident vehicles
                data.vehicles.forEach { vehicleData ->
                    if (validateVehicleData(vehicleData)) {
                        val vehicle = Vehicle(
                            vehicleId = "v_${vehicleData.id}",
                            plateNumber = vehicleData.plateNumber.trim(),
                            ownerName = vehicleData.ownerName.trim(),
                            unitNumber = "${vehicleData.dong ?: ""}동 ${vehicleData.ho ?: ""}호".trim(),
                            phoneNumber = vehicleData.ownerPhone?.trim(),
                            registrationDate = Date(),
                            status = if (vehicleData.isActive) "active" else "inactive",
                            vehicleType = "resident",
                            memo = "서버 동기화 - ${Date()}",
                            lastUpdated = Date(),
                            communityId = null
                        )
                        vehiclesToInsert.add(vehicle)
                    }
                }
                
                // Convert visitor vehicles
                data.visitorVehicles.forEach { visitorData ->
                    if (validateVisitorVehicleData(visitorData)) {
                        val vehicle = Vehicle(
                            vehicleId = "visitor_${visitorData.id}",
                            plateNumber = visitorData.plateNumber.trim(),
                            ownerName = visitorData.ownerName?.trim() ?: "방문자",
                            unitNumber = "${visitorData.dong ?: ""}동 ${visitorData.ho ?: ""}호 방문".trim(),
                            phoneNumber = visitorData.contactNumber?.trim(),
                            registrationDate = Date(),
                            status = if (visitorData.isActive) "active" else "inactive",
                            vehicleType = "guest",
                            memo = "방문차량 - 등록자: ${visitorData.registeredBy ?: "알 수 없음"}",
                            lastUpdated = Date(),
                            communityId = null
                        )
                        vehiclesToInsert.add(vehicle)
                    }
                }
                
                progressCallback?.onProgress(80, 100, "데이터 변환 완료")
                
                // Insert data in chunks to prevent memory issues
                val totalVehicles = vehiclesToInsert.size
                val chunks = vehiclesToInsert.chunked(CHUNK_SIZE)
                
                chunks.forEachIndexed { index, chunk ->
                    vehicleDao.insertVehicles(chunk)
                    
                    val progress = 80 + ((index + 1) * 15 / chunks.size)
                    progressCallback?.onProgress(
                        progress, 
                        100, 
                        "데이터 저장 중... (${(index + 1) * CHUNK_SIZE}/${totalVehicles})"
                    )
                    
                    // Small delay between chunks to prevent overwhelming the database
                    if (chunks.size > 1) delay(50)
                }
                
                Log.d(TAG, "Successfully processed and saved ${totalVehicles} vehicles in ${chunks.size} chunks")
                
                val message = if (totalVehicles == 0) {
                    "차량 데이터 동기화 완료: 현재 등록된 차량이 없습니다."
                } else {
                    "차량 데이터 동기화 완료: ${totalVehicles}대 차량 정보를 업데이트했습니다."
                }
                
                SyncResult(
                    success = true,
                    message = message,
                    vehicleCount = totalVehicles,
                    residentCount = syncResult.residentCount,
                    visitorVehicleCount = syncResult.visitorVehicleCount,
                    subAccountCount = syncResult.subAccountCount
                )
                
            } catch (e: Exception) {
                Log.e(TAG, "Data processing failed", e)
                SyncResult(
                    success = false,
                    message = "데이터 처리 중 오류 발생: ${e.message}"
                )
            }
        }
        
        private fun validateVehicleData(vehicleData: Any): Boolean {
            // Validate VehicleInfo data class
            return try {
                when (vehicleData) {
                    is VehicleInfo -> {
                        vehicleData.plateNumber.isNotBlank() && 
                        vehicleData.ownerName.isNotBlank()
                    }
                    else -> {
                        Log.w(TAG, "Invalid vehicle data type: ${vehicleData::class.simpleName}")
                        false
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Vehicle data validation failed", e)
                false
            }
        }
        
        private fun validateVisitorVehicleData(visitorData: Any): Boolean {
            // Validate VisitorVehicle data class
            return try {
                when (visitorData) {
                    is VisitorVehicle -> {
                        visitorData.plateNumber.isNotBlank()
                    }
                    else -> {
                        Log.w(TAG, "Invalid visitor data type: ${visitorData::class.simpleName}")
                        false
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Visitor vehicle data validation failed", e)
                false
            }
        }
        
        private suspend fun rollbackData(database: AppDatabase, backupVehicles: List<Vehicle>) {
            try {
                Log.d(TAG, "Rolling back to previous data (${backupVehicles.size} vehicles)")
                database.vehicleDao().deleteAllVehicles()
                database.vehicleDao().insertVehicles(backupVehicles)
                Log.d(TAG, "Rollback completed successfully")
            } catch (e: Exception) {
                Log.e(TAG, "Rollback failed", e)
            }
        }
        
        // Legacy function for backward compatibility
        suspend fun syncVehicleData(context: Context, token: String): SyncResult {
            return syncVehicleData(context, token, null)
        }
    }
}

data class SyncResult(
    val success: Boolean,
    val message: String,
    val vehicleCount: Int = 0,
    val residentCount: Int = 0,
    val visitorVehicleCount: Int = 0,
    val subAccountCount: Int = 0,
    val rawData: Any? = null // For internal use during processing
)