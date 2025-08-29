package org.aptgo.vehiclemanager.activities

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.aptgo.vehiclemanager.R
import org.aptgo.vehiclemanager.database.AppDatabase
import org.aptgo.vehiclemanager.databinding.ActivityMainBinding
import org.aptgo.vehiclemanager.network.NetworkModule
import org.aptgo.vehiclemanager.utils.PreferenceManager
import org.aptgo.vehiclemanager.utils.UserSession
import org.aptgo.vehiclemanager.utils.VehicleDataSync

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var preferenceManager: PreferenceManager
    private lateinit var database: AppDatabase
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        preferenceManager = PreferenceManager(this)
        database = AppDatabase.getDatabase(this)
        
        // UserSession이 비어있고 저장된 로그인 정보가 있다면 복원
        if (UserSession.user == null && preferenceManager.isLoggedIn()) {
            restoreUserSession()
        }
        
        setupToolbar()
        setupDashboard()
        syncVehicleData()
        loadStatistics()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "차량 관리 시스템"
        supportActionBar?.subtitle = UserSession.user?.communityName ?: ""
    }
    
    private fun setupDashboard() {
        binding.cardCameraScan.setOnClickListener {
            startActivity(Intent(this, CameraScanActivity::class.java))
        }
        
        binding.cardManualSearch.setOnClickListener {
            // 데이터 보기 기능으로 변경
            startActivity(Intent(this, VehicleDataViewActivity::class.java))
        }
        
        binding.cardHistory.setOnClickListener {
            // 데이터 새로고침 기능으로 변경 - VehicleDataViewActivity에서 진행상황과 함께 수행
            refreshVehicleDataWithProgress()
        }
        
        binding.cardReport.setOnClickListener {
            startActivity(Intent(this, ReportActivity::class.java))
        }
        
        binding.cardSettings.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        
        binding.btnQuickScan.setOnClickListener {
            startActivity(Intent(this, CameraScanActivity::class.java))
        }
        
        // 기존 개별 버튼들은 그리드 아이콘으로 통합됨
    }
    
    
    private fun syncVehicleData() {
        lifecycleScope.launch {
            try {
                val token = preferenceManager.getAuthToken() ?: return@launch
                val communityId = UserSession.user?.communityId
                
                val response = NetworkModule.apiService.getVehicles(
                    "Bearer $token",
                    communityId
                )
                
                if (response.isSuccessful && response.body()?.success == true) {
                    val vehicles = response.body()!!.vehicles
                    
                    // Clear and update local database
                    database.vehicleDao().deleteAllVehicles()
                    database.vehicleDao().insertVehicles(vehicles)
                    
                    Toast.makeText(this@MainActivity, 
                        "${vehicles.size}개 차량 정보 동기화 완료", 
                        Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, 
                    "데이터 동기화 실패: 오프라인 모드", 
                    Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun loadStatistics() {
        lifecycleScope.launch {
            try {
                val todayTotal = database.scanHistoryDao().getTodayScansCount()
                val todayAuto = database.scanHistoryDao().getTodayScansCountByType("auto")
                val todayManual = database.scanHistoryDao().getTodayScansCountByType("manual")
                val vehicleCount = database.vehicleDao().getVehicleCount()
                
                binding.textTodayScans.text = "오늘 스캔: $todayTotal"
                binding.textAutoScans.text = "자동: $todayAuto"
                binding.textManualScans.text = "수동: $todayManual"
                binding.textTotalVehicles.text = "등록 차량: $vehicleCount"
                
                // Calculate recognition rate
                if (todayTotal > 0) {
                    val recognitionRate = (todayAuto.toFloat() / todayTotal * 100).toInt()
                    binding.textRecognitionRate.text = "인식률: $recognitionRate%"
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_sync -> {
                syncVehicleData()
                true
            }
            R.id.action_logout -> {
                performLogout()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    private fun refreshVehicleDataWithProgress() {
        val user = UserSession.user
        android.util.Log.d("MainActivity", "refreshVehicleDataWithProgress - User: ${user?.username}")
        
        if (user?.canRefreshVehicleData() != true) {
            Toast.makeText(this, "차량 데이터 새로고침 권한이 없습니다.", Toast.LENGTH_SHORT).show()
            return
        }
        
        // VehicleDataViewActivity를 시작하여 진행상황과 함께 다운로드 수행
        val intent = Intent(this, VehicleDataViewActivity::class.java)
        intent.putExtra("auto_refresh", true) // 자동 새로고침 플래그
        startActivity(intent)
    }
    
    private fun refreshVehicleDataFromServer() {
        val user = UserSession.user
        android.util.Log.d("MainActivity", "refreshVehicleDataFromServer - User: ${user?.username}")
        
        if (user?.canRefreshVehicleData() != true) {
            Toast.makeText(this, "차량 데이터 새로고침 권한이 없습니다.", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                // 사용자에게 진행 상황 알림
                Toast.makeText(this@MainActivity, "차량 데이터를 서버에서 새로고침 중...", Toast.LENGTH_SHORT).show()
                
                val token = preferenceManager.getAuthToken()
                android.util.Log.d("MainActivity", "Token from preference: $token")
                
                if (token == null) {
                    Toast.makeText(this@MainActivity, "인증 토큰이 없습니다. 다시 로그인해주세요.", Toast.LENGTH_LONG).show()
                    return@launch
                }
                
                val syncResult = org.aptgo.vehiclemanager.utils.VehicleDataSync.syncVehicleData(this@MainActivity, token)
                
                if (syncResult.success) {
                    Toast.makeText(
                        this@MainActivity, 
                        syncResult.message, 
                        Toast.LENGTH_LONG
                    ).show()
                    
                    // 통계 새로고침
                    loadStatistics()
                    
                } else {
                    Toast.makeText(this@MainActivity, "데이터 새로고침 실패: ${syncResult.message}", Toast.LENGTH_LONG).show()
                }
                
            } catch (e: Exception) {
                e.printStackTrace()
                Toast.makeText(
                    this@MainActivity, 
                    "데이터 새로고침 중 오류 발생: ${e.message}", 
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    private fun performLogout() {
        preferenceManager.clearLoginInfo()
        UserSession.user = null
        
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
    }
    
    override fun onResume() {
        super.onResume()
        loadStatistics()
        // 통계 정보만 업데이트
    }
    
    private fun restoreUserSession() {
        // 저장된 정보로 UserSession 복원
        val savedUser = preferenceManager.getSavedUser()
        
        if (savedUser != null) {
            UserSession.user = savedUser
            android.util.Log.d("MainActivity", "User session restored - username: ${savedUser.username}, type: ${savedUser.user_type}, manager: ${savedUser.is_manager}")
            
            // 서버에서 최신 사용자 정보를 다시 가져오도록 시도
            refreshUserInfo()
        } else {
            android.util.Log.d("MainActivity", "No saved user found in preferences")
        }
    }
    
    private fun refreshUserInfo() {
        lifecycleScope.launch {
            try {
                val token = preferenceManager.getAuthToken() ?: return@launch
                // 여기에 사용자 정보를 다시 가져오는 API 호출을 추가할 수 있음
                // 현재는 로그만 출력
                android.util.Log.d("MainActivity", "User session restored from preferences")
            } catch (e: Exception) {
                android.util.Log.e("MainActivity", "Failed to refresh user info", e)
            }
        }
    }
}