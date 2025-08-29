package org.aptgo.vehiclemanager.activities

import android.Manifest
import android.content.Intent
import android.media.MediaPlayer
import android.os.Bundle
import android.util.Size
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.korean.KoreanTextRecognizerOptions
import com.permissionx.guolindev.PermissionX
import kotlinx.coroutines.launch
import org.aptgo.vehiclemanager.R
import org.aptgo.vehiclemanager.database.AppDatabase
import org.aptgo.vehiclemanager.databinding.ActivityCameraScanBinding
import org.aptgo.vehiclemanager.models.ScanHistory
import org.aptgo.vehiclemanager.models.Vehicle
import org.aptgo.vehiclemanager.utils.PlateNumberValidator
import org.aptgo.vehiclemanager.utils.PreferenceManager
import org.aptgo.vehiclemanager.network.NetworkModule
import org.aptgo.vehiclemanager.utils.UserSession
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraScanActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityCameraScanBinding
    private lateinit var database: AppDatabase
    private lateinit var preferenceManager: PreferenceManager
    private lateinit var cameraExecutor: ExecutorService
    
    private var imageCapture: ImageCapture? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var isScanning = true
    private var isContinuousMode = true
    private var lastScannedPlate = ""
    private var scanConfidence = 0f
    
    private val textRecognizer = TextRecognition.getClient(
        KoreanTextRecognizerOptions.Builder().build()
    )
    
    private var successSound: MediaPlayer? = null
    private var warningSound: MediaPlayer? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCameraScanBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        database = AppDatabase.getDatabase(this)
        preferenceManager = PreferenceManager(this)
        cameraExecutor = Executors.newSingleThreadExecutor()
        
        setupSounds()
        setupUI()
        requestCameraPermission()
    }
    
    private fun setupSounds() {
        try {
            successSound = MediaPlayer.create(this, R.raw.success_beep)
            warningSound = MediaPlayer.create(this, R.raw.warning_alarm)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun setupUI() {
        binding.btnManualInput.setOnClickListener {
            switchToManualMode()
        }
        
        binding.btnFlash.setOnClickListener {
            toggleFlash()
        }
        
        binding.btnScanMode.setOnClickListener {
            toggleScanMode()
        }
        
        binding.btnCapture.setOnClickListener {
            if (!isContinuousMode) {
                captureAndAnalyze()
            }
        }
        
        updateScanModeUI()
    }
    
    private fun requestCameraPermission() {
        PermissionX.init(this)
            .permissions(Manifest.permission.CAMERA)
            .request { allGranted, _, _ ->
                if (allGranted) {
                    startCamera()
                } else {
                    Toast.makeText(this, "카메라 권한이 필요합니다", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }
    }
    
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        
        cameraProviderFuture.addListener({
            cameraProvider = cameraProviderFuture.get()
            
            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(binding.previewView.surfaceProvider)
                }
            
            imageCapture = ImageCapture.Builder()
                .setTargetResolution(Size(1920, 1080))
                .build()
            
            val imageAnalyzer = ImageAnalysis.Builder()
                .setTargetResolution(Size(1920, 1080))
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor, PlateNumberAnalyzer())
                }
            
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            
            try {
                cameraProvider?.unbindAll()
                
                camera = if (isContinuousMode) {
                    cameraProvider?.bindToLifecycle(
                        this, cameraSelector, preview, imageCapture, imageAnalyzer
                    )
                } else {
                    cameraProvider?.bindToLifecycle(
                        this, cameraSelector, preview, imageCapture
                    )
                }
                
            } catch (exc: Exception) {
                Toast.makeText(this, "카메라 시작 실패", Toast.LENGTH_SHORT).show()
            }
            
        }, ContextCompat.getMainExecutor(this))
    }
    
    private fun captureAndAnalyze() {
        val imageCapture = imageCapture ?: return
        
        imageCapture.takePicture(
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageCapturedCallback() {
                @androidx.camera.core.ExperimentalGetImage
                override fun onCaptureSuccess(image: ImageProxy) {
                    processImage(image)
                }
                
                override fun onError(exception: ImageCaptureException) {
                    Toast.makeText(this@CameraScanActivity, 
                        "캡처 실패: ${exception.message}", 
                        Toast.LENGTH_SHORT).show()
                }
            }
        )
    }
    
    @androidx.camera.core.ExperimentalGetImage
    private fun processImage(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
            
            textRecognizer.process(image)
                .addOnSuccessListener { visionText ->
                    val plateNumber = PlateNumberValidator.extractPlateNumber(visionText.text)
                    if (plateNumber != null) {
                        scanConfidence = PlateNumberValidator.calculateConfidence(visionText.text)
                        handlePlateDetected(plateNumber)
                    } else {
                        showNoPlateDetected()
                    }
                }
                .addOnFailureListener { e ->
                    Toast.makeText(this, "OCR 실패: ${e.message}", Toast.LENGTH_SHORT).show()
                }
                .addOnCompleteListener {
                    imageProxy.close()
                }
        } else {
            imageProxy.close()
        }
    }
    
    private fun handlePlateDetected(plateNumber: String) {
        if (!isScanning) return
        
        // Avoid duplicate scanning
        if (plateNumber == lastScannedPlate) {
            return
        }
        
        lastScannedPlate = plateNumber
        isScanning = false
        
        binding.textPlateNumber.text = plateNumber
        binding.textConfidence.text = "신뢰도: ${(scanConfidence * 100).toInt()}%"
        
        lifecycleScope.launch {
            checkVehicle(plateNumber)
        }
        
        // Re-enable scanning after 3 seconds in continuous mode
        if (isContinuousMode) {
            binding.previewView.postDelayed({
                isScanning = true
                lastScannedPlate = ""
            }, 3000)
        }
    }
    
    private suspend fun checkVehicle(plateNumber: String) {
        val vehicle = database.vehicleDao().getVehicleByPlateNumber(plateNumber)
        
        runOnUiThread {
            if (vehicle != null) {
                showRegisteredVehicle(vehicle, plateNumber)
            } else {
                showUnregisteredVehicle(plateNumber)
            }
        }
        
        // Save scan history
        saveScanHistory(plateNumber, vehicle)
    }
    
    private fun showRegisteredVehicle(vehicle: Vehicle, plateNumber: String) {
        val currentTime = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        
        binding.layoutResult.visibility = View.VISIBLE
        
        binding.textResultTitle.text = "등록차량 OK"
        binding.textResultDetails.text = """
            차량번호: $plateNumber
            인식시간: $currentTime
            소유자: ${vehicle.ownerName}
            동/호수: ${vehicle.unitNumber}
            연락처: ${vehicle.phoneNumber ?: "없음"}
            유형: ${getVehicleTypeText(vehicle.vehicleType)}
        """.trimIndent()
        
        binding.btnAction1.visibility = View.VISIBLE
        binding.btnAction1.text = "확인"
        binding.btnAction1.setOnClickListener {
            binding.layoutResult.visibility = View.GONE
            isScanning = true
        }
        
        binding.btnAction2.visibility = View.VISIBLE
        binding.btnAction2.text = "보고서 전송"
        binding.btnAction2.setOnClickListener {
            sendScanReport(plateNumber, true, currentTime, null)
        }
        
        successSound?.start()
    }
    
    private fun showUnregisteredVehicle(plateNumber: String) {
        val currentTime = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        val maskedPlateNumber = maskPlateNumber(plateNumber)
        
        binding.layoutResult.visibility = View.VISIBLE
        
        binding.textResultTitle.text = "미등록차량"
        binding.textResultDetails.text = """
            차량번호: $maskedPlateNumber
            인식시간: $currentTime
            
            조치사항을 선택하세요
        """.trimIndent()
        
        binding.btnAction1.visibility = View.VISIBLE
        binding.btnAction1.text = "조치사항 선택"
        binding.btnAction1.setOnClickListener {
            showActionSelectionDialog(plateNumber, currentTime)
        }
        
        binding.btnAction2.visibility = View.VISIBLE
        binding.btnAction2.text = "사진 촬영"
        binding.btnAction2.setOnClickListener {
            capture720pPhoto(plateNumber, currentTime)
        }
        
        warningSound?.start()
    }
    
    private fun showNoPlateDetected() {
        binding.textPlateNumber.text = "번호판 감지 실패"
        binding.textConfidence.text = "신뢰도: 낮음"
        
        Toast.makeText(this, "번호판을 인식할 수 없습니다", Toast.LENGTH_SHORT).show()
    }
    
    private suspend fun saveScanHistory(plateNumber: String, vehicle: Vehicle?) {
        val scanHistory = ScanHistory(
            plateNumber = plateNumber,
            scanType = "auto",
            scanDate = Date(),
            isRegistered = vehicle != null,
            vehicleId = vehicle?.vehicleId,
            location = "주차장",
            actionTaken = null,
            photoPath = null,
            notes = "신뢰도: ${(scanConfidence * 100).toInt()}%",
            userId = preferenceManager.getSavedUsername() ?: "",
            synced = false
        )
        
        database.scanHistoryDao().insertScanHistory(scanHistory)
    }
    
    private fun recordAction(plateNumber: String, action: String) {
        lifecycleScope.launch {
            val scanHistory = ScanHistory(
                plateNumber = plateNumber,
                scanType = "auto",
                scanDate = Date(),
                isRegistered = false,
                vehicleId = null,
                location = "주차장",
                actionTaken = action,
                photoPath = null,
                notes = null,
                userId = preferenceManager.getSavedUsername() ?: "",
                synced = false
            )
            
            database.scanHistoryDao().insertScanHistory(scanHistory)
            
            runOnUiThread {
                Toast.makeText(this@CameraScanActivity, "$action 완료", Toast.LENGTH_SHORT).show()
                binding.layoutResult.visibility = View.GONE
                isScanning = true
            }
        }
    }
    
    private fun captureEvidence(plateNumber: String) {
        // TODO: Implement photo capture and save
        Toast.makeText(this, "사진 촬영 기능 구현 예정", Toast.LENGTH_SHORT).show()
    }
    
    private fun switchToManualMode() {
        val intent = Intent(this, ManualSearchActivity::class.java)
        startActivity(intent)
    }
    
    private fun toggleFlash() {
        camera?.let {
            val hasFlash = it.cameraInfo.hasFlashUnit()
            if (hasFlash) {
                val isFlashOn = it.cameraInfo.torchState.value == TorchState.ON
                it.cameraControl.enableTorch(!isFlashOn)
                binding.btnFlash.text = if (!isFlashOn) "플래시 OFF" else "플래시 ON"
            }
        }
    }
    
    private fun toggleScanMode() {
        isContinuousMode = !isContinuousMode
        updateScanModeUI()
        
        // Restart camera with new mode
        cameraProvider?.unbindAll()
        startCamera()
    }
    
    private fun updateScanModeUI() {
        binding.btnScanMode.text = if (isContinuousMode) "연속 스캔" else "단일 캡처"
        binding.btnCapture.visibility = if (isContinuousMode) View.GONE else View.VISIBLE
    }
    
    private fun getVehicleTypeText(type: String): String {
        return when (type) {
            "resident" -> "입주민"
            "guest" -> "방문"
            "permitted" -> "허가"
            else -> type
        }
    }
    
    private fun maskPlateNumber(plateNumber: String): String {
        return if (plateNumber.length >= 4) {
            val visible = plateNumber.substring(0, 2)
            val masked = "*".repeat(plateNumber.length - 2)
            "$visible$masked"
        } else {
            plateNumber
        }
    }
    
    private fun showActionSelectionDialog(plateNumber: String, currentTime: String) {
        val actions = arrayOf("스티커발부", "주의전화", "기타")
        
        val builder = android.app.AlertDialog.Builder(this)
        builder.setTitle("조치사항 선택")
        builder.setItems(actions) { _, which ->
            val selectedAction = actions[which]
            recordActionWithReport(plateNumber, selectedAction, currentTime)
        }
        builder.show()
    }
    
    private fun capture720pPhoto(plateNumber: String, currentTime: String) {
        val imageCapture = imageCapture ?: return
        
        val photoFile = File(
            getExternalFilesDir("photos"),
            "unregistered_${plateNumber}_${System.currentTimeMillis()}.jpg"
        )
        
        val outputFileOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()
        
        imageCapture.takePicture(
            outputFileOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    Toast.makeText(this@CameraScanActivity, 
                        "720P 사진 저장 완료: ${photoFile.name}", 
                        Toast.LENGTH_SHORT).show()
                    
                    // Show dialog to select action after photo is taken
                    showActionSelectionDialog(plateNumber, currentTime)
                }
                
                override fun onError(exception: ImageCaptureException) {
                    Toast.makeText(this@CameraScanActivity,
                        "사진 촬영 실패: ${exception.message}",
                        Toast.LENGTH_SHORT).show()
                }
            }
        )
    }
    
    private fun recordActionWithReport(plateNumber: String, action: String, currentTime: String) {
        lifecycleScope.launch {
            // Save to local database
            val scanHistory = ScanHistory(
                plateNumber = plateNumber,
                scanType = "auto",
                scanDate = Date(),
                isRegistered = false,
                vehicleId = null,
                location = "주차장",
                actionTaken = action,
                photoPath = null,
                notes = "조치사항: $action",
                userId = preferenceManager.getSavedUsername() ?: "",
                synced = false
            )
            
            database.scanHistoryDao().insertScanHistory(scanHistory)
            
            // Send report to server
            sendScanReport(plateNumber, false, currentTime, action)
            
            runOnUiThread {
                Toast.makeText(this@CameraScanActivity, "$action 완료 및 보고서 전송", Toast.LENGTH_SHORT).show()
                binding.layoutResult.visibility = View.GONE
                isScanning = true
            }
        }
    }
    
    private fun sendScanReport(plateNumber: String, isRegistered: Boolean, time: String, action: String?) {
        lifecycleScope.launch {
            try {
                val token = preferenceManager.getAuthToken()
                if (token.isNullOrEmpty()) {
                    runOnUiThread {
                        Toast.makeText(this@CameraScanActivity, "인증 토큰이 없습니다", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                val reportData = mapOf(
                    "plate_number" to plateNumber,
                    "is_registered" to isRegistered,
                    "recognition_time" to time,
                    "action_taken" to (action ?: ""),
                    "location" to "주차장",
                    "user_id" to (preferenceManager.getSavedUsername() ?: ""),
                    "timestamp" to SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())
                )
                
                // Send to ANPR reports API endpoint
                val response = NetworkModule.apiService.sendScanReport(reportData)
                
                runOnUiThread {
                    Toast.makeText(this@CameraScanActivity, "보고서가 서버로 전송되었습니다", Toast.LENGTH_SHORT).show()
                }
                
            } catch (e: Exception) {
                android.util.Log.e("CameraScanActivity", "보고서 전송 실패", e)
                runOnUiThread {
                    Toast.makeText(this@CameraScanActivity, "보고서 전송 실패: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private inner class PlateNumberAnalyzer : ImageAnalysis.Analyzer {
        @androidx.camera.core.ExperimentalGetImage
        override fun analyze(imageProxy: ImageProxy) {
            if (!isScanning || !isContinuousMode) {
                imageProxy.close()
                return
            }
            
            processImage(imageProxy)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        successSound?.release()
        warningSound?.release()
    }
}