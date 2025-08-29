package org.aptgo.vehiclemanager.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.Job
import kotlin.math.max
import kotlin.math.min
import org.aptgo.vehiclemanager.R
import org.aptgo.vehiclemanager.adapters.VehicleCompactAdapter
import org.aptgo.vehiclemanager.database.AppDatabase
import org.aptgo.vehiclemanager.databinding.ActivityVehicleDataViewBinding
import org.aptgo.vehiclemanager.models.Vehicle
import org.aptgo.vehiclemanager.network.NetworkModule
import org.aptgo.vehiclemanager.utils.PreferenceManager
import java.text.SimpleDateFormat
import java.util.*

class VehicleDataViewActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityVehicleDataViewBinding
    private lateinit var database: AppDatabase
    private lateinit var vehicleAdapter: VehicleCompactAdapter
    private lateinit var scaleGestureDetector: ScaleGestureDetector
    private lateinit var preferenceManager: PreferenceManager
    
    // 줌 관련 변수들
    private var scaleFactor = 1.0f
    private val minScale = 0.5f
    private val maxScale = 3.0f
    
    // 다운로드 진행상황 추적
    private var downloadJob: Job? = null
    private var downloadStartTime = 0L
    private var totalDataSize = 0L
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityVehicleDataViewBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        database = AppDatabase.getDatabase(this)
        preferenceManager = PreferenceManager(this)
        
        setupToolbar()
        setupZoomGestures()
        setupRecyclerView()
        setupSwipeRefresh()
        setupDownloadProgress()
        
        // 자동 새로고침 모드 처리
        val autoRefresh = intent.getBooleanExtra("auto_refresh", false)
        if (autoRefresh) {
            // 자동으로 다운로드 시작
            loadVehicleData()
        } else {
            // 기존 데이터만 로드
            loadExistingData()
        }
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.apply {
            title = "차량 데이터 보기"
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
        
        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }
    
    private fun setupZoomGestures() {
        scaleGestureDetector = ScaleGestureDetector(this, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                
                // 최소/최대 스케일 제한
                scaleFactor = max(minScale, min(scaleFactor, maxScale))
                
                // RecyclerView에 스케일 적용
                binding.recyclerView.scaleX = scaleFactor
                binding.recyclerView.scaleY = scaleFactor
                
                // 스케일에 따라 크기 조정
                val layoutParams = binding.recyclerView.layoutParams
                val originalWidth = resources.displayMetrics.widthPixels
                layoutParams.width = (originalWidth * scaleFactor).toInt()
                binding.recyclerView.layoutParams = layoutParams
                
                android.util.Log.d("VehicleDataViewActivity", "Scale factor: $scaleFactor")
                return true
            }
        })
        
        // HorizontalScrollView에 터치 리스너 추가
        binding.horizontalScrollView.setOnTouchListener { _, event ->
            scaleGestureDetector.onTouchEvent(event)
            false // 다른 터치 이벤트도 처리할 수 있도록 false 반환
        }
    }
    
    private fun setupRecyclerView() {
        vehicleAdapter = VehicleCompactAdapter { vehicle ->
            // Handle vehicle item click - could show detail view or other actions
            android.util.Log.d("VehicleDataViewActivity", "Vehicle clicked: ${vehicle.plateNumber}")
        }
        
        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(this@VehicleDataViewActivity)
            adapter = vehicleAdapter
            
            // 대용량 데이터셋을 위한 성능 최적화
            setHasFixedSize(true)
            setItemViewCacheSize(20) // 캐시 크기 증가
            isDrawingCacheEnabled = true
            drawingCacheQuality = View.DRAWING_CACHE_QUALITY_LOW
        }
    }
    
    private fun setupSwipeRefresh() {
        // 새로고침 기능은 메인 액티비티의 스캔기록 버튼으로 이전됨
    }
    
    private fun setupDownloadProgress() {
        // 취소 버튼 클릭 처리
        binding.cancelDownloadButton.setOnClickListener {
            cancelDownload()
        }
    }
    
    
    private fun loadVehicleData() {
        downloadJob = lifecycleScope.launch {
            try {
                showDownloadProgress(true)
                updateProgressText("서버 연결 중...", 0)
                
                // 서버에서 최신 데이터 가져오기 (진행상황 추적)
                refreshDataFromServer()
                
                val vehicles = database.vehicleDao().getAllVehicles()
                
                vehicles.collect { vehicleList ->
                    // 대용량 데이터셋을 위한 최적화된 처리
                    android.util.Log.d("VehicleDataViewActivity", "Loading ${vehicleList.size} vehicles")
                    
                    // UI 업데이트는 메인 스레드에서 배치 처리
                    updateUI(vehicleList)
                    
                    // 로딩 완료 처리
                    completeDataLoading()
                }
                
            } catch (e: Exception) {
                android.util.Log.e("VehicleDataViewActivity", "Error loading vehicle data", e)
                completeDataLoadingWithError()
            }
        }
    }
    
    private fun loadExistingData() {
        lifecycleScope.launch {
            try {
                showLoading(true)
                
                val vehicles = database.vehicleDao().getAllVehicles()
                
                vehicles.collect { vehicleList ->
                    android.util.Log.d("VehicleDataViewActivity", "Loading existing ${vehicleList.size} vehicles")
                    updateUI(vehicleList)
                    showLoading(false)
                }
                
            } catch (e: Exception) {
                android.util.Log.e("VehicleDataViewActivity", "Error loading existing vehicle data", e)
                showLoading(false)
                showEmptyState(true)
            }
        }
    }
    
    private suspend fun refreshDataFromServer() {
        try {
            downloadStartTime = System.currentTimeMillis()
            updateProgressText("로그인 토큰 확인 중...", 5)
            
            // PreferenceManager를 사용하여 올바른 토큰 가져오기
            val token = preferenceManager.getAuthToken()
            
            if (token.isNullOrEmpty()) {
                updateProgressText("로그인 토큰이 없습니다. 다시 로그인해주세요.", 0)
                android.util.Log.w("VehicleDataViewActivity", "No auth token found - user needs to login again")
                return
            }
            
            android.util.Log.d("VehicleDataViewActivity", "Auth token found: ${token.substring(0, 10)}...")
            
            updateProgressText("서버에 요청 중...", 15)
            delay(500) // 시각적 피드백을 위한 지연
            
            // 서버 API 호출 - Authorization 헤더 로그 추가
            android.util.Log.d("VehicleDataViewActivity", "Calling API with token: Bearer ${token.substring(0, 10)}...")
            val response = NetworkModule.apiService.getComprehensiveVehicleData("Bearer $token")
            android.util.Log.d("VehicleDataViewActivity", "API response code: ${response.code()}")
            
            if (response.isSuccessful) {
                val comprehensiveData = response.body()
                
                if (comprehensiveData?.success == true) {
                    val vehicleCount = comprehensiveData.vehicles.size
                    val visitorVehicleCount = comprehensiveData.visitorVehicles.size
                    val totalCount = vehicleCount + visitorVehicleCount
                    updateProgressText("데이터 수신 완료: 차량 ${vehicleCount}대, 방문차량 ${visitorVehicleCount}대", 60)
                    
                    // Response body의 크기 계산 (추정)
                    totalDataSize = (response.raw().body?.contentLength() ?: 0L)
                    if (totalDataSize == 0L) {
                        // Content-Length가 없으면 추정값 사용
                        totalDataSize = (totalCount * 200L) // 차량당 약 200바이트 추정
                    }
                    updateDownloadSize(totalDataSize)
                    
                    android.util.Log.d("VehicleDataViewActivity", 
                        "Server sync successful: ${vehicleCount} vehicles, ${visitorVehicleCount} visitor vehicles from server")
                    
                    updateProgressText("데이터 변환 중...", 70)
                    delay(200)
                    
                    val allVehicles = mutableListOf<Vehicle>()
                    
                    // 일반 차량 데이터 변환
                    val vehicleList = comprehensiveData.vehicles.mapIndexed { index, serverVehicle ->
                        // 변환 진행상황 업데이트
                        val progress = 70 + ((index + 1) * 10 / totalCount)
                        if (index % 10 == 0) { // 10개마다 업데이트
                            updateProgressText("차량 변환 중: ${index + 1}/${vehicleCount}", progress)
                        }
                        
                        Vehicle(
                            vehicleId = "v_${serverVehicle.id}",
                            plateNumber = serverVehicle.plateNumber,
                            ownerName = serverVehicle.ownerName,
                            unitNumber = "${serverVehicle.dong ?: ""}-${serverVehicle.ho ?: ""}",
                            phoneNumber = serverVehicle.ownerPhone,
                            registrationDate = java.util.Date(),
                            status = if (serverVehicle.isActive) "active" else "inactive",
                            vehicleType = serverVehicle.vehicleType,
                            memo = null,
                            lastUpdated = java.util.Date(),
                            communityId = null
                        )
                    }
                    allVehicles.addAll(vehicleList)
                    
                    // 방문차량 데이터 변환
                    val visitorVehicleList = comprehensiveData.visitorVehicles.mapIndexed { index, visitorVehicle ->
                        // 변환 진행상황 업데이트
                        val progress = 80 + ((index + 1) * 10 / totalCount)
                        if (index % 10 == 0) { // 10개마다 업데이트
                            updateProgressText("방문차량 변환 중: ${index + 1}/${visitorVehicleCount}", progress)
                        }
                        
                        Vehicle(
                            vehicleId = "visitor_${visitorVehicle.id}",
                            plateNumber = visitorVehicle.plateNumber,
                            ownerName = visitorVehicle.ownerName ?: "방문자",
                            unitNumber = "${visitorVehicle.dong ?: ""}-${visitorVehicle.ho ?: ""} 방문",
                            phoneNumber = visitorVehicle.contactNumber,
                            registrationDate = java.util.Date(),
                            status = if (visitorVehicle.isActive) "active" else "inactive",
                            vehicleType = "guest",  // 방문차량은 guest 타입으로
                            memo = "등록자: ${visitorVehicle.registeredBy ?: "알 수 없음"}",
                            lastUpdated = java.util.Date(),
                            communityId = null
                        )
                    }
                    allVehicles.addAll(visitorVehicleList)
                    
                    updateProgressText("데이터베이스 저장 중...", 90)
                    
                    // 기존 데이터 삭제 후 새 데이터 삽입
                    database.vehicleDao().deleteAllVehicles()
                    database.vehicleDao().insertVehicles(allVehicles)
                    
                    updateProgressText("완료: 차량 ${vehicleCount}대, 방문차량 ${visitorVehicleCount}대 동기화", 100)
                    delay(1000) // 완료 메시지 표시
                    
                    android.util.Log.d("VehicleDataViewActivity", 
                        "Successfully synced ${allVehicles.size} vehicles (${vehicleCount} regular + ${visitorVehicleCount} visitor) to local database")
                        
                } else {
                    updateProgressText("서버 응답 오류: ${comprehensiveData?.message}", 0)
                    android.util.Log.w("VehicleDataViewActivity", 
                        "Server response not successful: ${comprehensiveData?.message}")
                    android.util.Log.w("VehicleDataViewActivity", 
                        "Full response: $comprehensiveData")
                }
            } else {
                updateProgressText("API 호출 실패: ${response.code()}", 0)
                android.util.Log.e("VehicleDataViewActivity", 
                    "Server API call failed: ${response.code()} - ${response.message()}")
                try {
                    val errorBody = response.errorBody()?.string()
                    android.util.Log.e("VehicleDataViewActivity", "Error body: $errorBody")
                } catch (e: Exception) {
                    android.util.Log.e("VehicleDataViewActivity", "Could not read error body", e)
                }
            }
            
        } catch (e: Exception) {
            updateProgressText("오류: ${e.message}", 0)
            android.util.Log.e("VehicleDataViewActivity", "Error syncing with server", e)
        }
    }
    
    private fun completeDataLoading() {
        showDownloadProgress(false)
    }
    
    private fun completeDataLoadingWithError() {
        showDownloadProgress(false)
        showEmptyState(true)
    }
    
    private fun cancelDownload() {
        downloadJob?.cancel()
        showDownloadProgress(false)
        updateProgressText("다운로드가 취소되었습니다", 0)
        android.util.Log.d("VehicleDataViewActivity", "Download cancelled by user")
    }
    
    private fun updateUI(vehicles: List<Vehicle>) {
        if (vehicles.isEmpty()) {
            showEmptyState(true)
            hideStatistics()
        } else {
            showEmptyState(false)
            updateVehicleList(vehicles)
            updateStatistics(vehicles)
        }
    }
    
    private fun updateVehicleList(vehicles: List<Vehicle>) {
        vehicleAdapter.submitList(vehicles)
    }
    
    private fun updateStatistics(vehicles: List<Vehicle>) {
        val totalVehicles = vehicles.size
        val residentCount = vehicles.count { it.vehicleType == "resident" }
        val guestCount = vehicles.count { it.vehicleType == "guest" }
        val permittedCount = vehicles.count { it.vehicleType == "permitted" }
        val visitorCount = guestCount + permittedCount
        
        // 가장 최근 업데이트 시간 찾기
        val lastUpdated = vehicles.maxByOrNull { it.lastUpdated }?.lastUpdated
        val lastUpdatedStr = lastUpdated?.let { 
            SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(it)
        } ?: "-"
        
        binding.apply {
            textVehicleCount.text = "차량: ${totalVehicles}대"
            textResidentCount.text = "입주민: ${residentCount}명"
            textVisitorCount.text = "방문차량: ${visitorCount}대"
            textLastUpdated.text = "최종 업데이트: $lastUpdatedStr"
            
            // 통계 카드 표시
            statisticsCard.visibility = View.VISIBLE
        }
    }
    
    private fun showEmptyState(show: Boolean) {
        binding.emptyStateLayout.visibility = if (show) View.VISIBLE else View.GONE
        binding.recyclerView.visibility = if (show) View.GONE else View.VISIBLE
    }
    
    private fun hideStatistics() {
        binding.statisticsCard.visibility = View.GONE
    }
    
    private fun showLoading(show: Boolean) {
        binding.progressBar.visibility = if (show) View.VISIBLE else View.GONE
    }
    
    private fun showDownloadProgress(show: Boolean) {
        binding.downloadProgressCard.visibility = if (show) View.VISIBLE else View.GONE
        if (!show) {
            // 리셋
            binding.downloadProgressBar.progress = 0
            binding.downloadProgressText.text = "준비 중..."
            binding.downloadSizeText.text = "크기: 0 KB"
            binding.downloadSpeedText.text = "속도: 0 KB/s"
        }
    }
    
    private fun updateProgressText(message: String, progress: Int) {
        binding.downloadProgressText.text = message
        binding.downloadProgressBar.progress = progress
        
        // 속도 계산 및 표시
        if (downloadStartTime > 0 && totalDataSize > 0) {
            val elapsed = (System.currentTimeMillis() - downloadStartTime) / 1000.0
            if (elapsed > 0) {
                val bytesTransferred = (totalDataSize * progress / 100.0)
                val speed = (bytesTransferred / elapsed / 1024).toInt() // KB/s
                binding.downloadSpeedText.text = "속도: ${speed} KB/s"
            }
        }
    }
    
    private fun updateDownloadSize(bytes: Long) {
        val kb = (bytes / 1024.0).toInt()
        binding.downloadSizeText.text = "크기: ${kb} KB"
    }
    
    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_vehicle_data_view, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_reset_zoom -> {
                resetZoom()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    private fun resetZoom() {
        scaleFactor = 1.0f
        binding.recyclerView.scaleX = scaleFactor
        binding.recyclerView.scaleY = scaleFactor
        
        // 원본 크기로 복원
        val layoutParams = binding.recyclerView.layoutParams
        layoutParams.width = resources.displayMetrics.widthPixels
        binding.recyclerView.layoutParams = layoutParams
        
        android.util.Log.d("VehicleDataViewActivity", "Zoom reset to 1.0x")
    }
    
    override fun onSupportNavigateUp(): Boolean {
        // 다운로드 진행 중이면 취소
        if (downloadJob?.isActive == true) {
            cancelDownload()
        }
        finish()
        return true
    }
    
    override fun onDestroy() {
        // 액티비티 종료 시 다운로드 작업 취소
        downloadJob?.cancel()
        super.onDestroy()
    }
}