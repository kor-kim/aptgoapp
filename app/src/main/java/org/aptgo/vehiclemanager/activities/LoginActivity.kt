package org.aptgo.vehiclemanager.activities

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.aptgo.vehiclemanager.databinding.ActivityLoginBinding
import org.aptgo.vehiclemanager.network.LoginRequest
import org.aptgo.vehiclemanager.network.NetworkModule
import org.aptgo.vehiclemanager.utils.PreferenceManager
import org.aptgo.vehiclemanager.utils.UserSession
import org.aptgo.vehiclemanager.utils.VehicleDataSync

class LoginActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private lateinit var preferenceManager: PreferenceManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        android.util.Log.d("LoginActivity", "onCreate called")
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        preferenceManager = PreferenceManager(this)
        
        // Check if already logged in
        if (preferenceManager.isLoggedIn()) {
            android.util.Log.d("LoginActivity", "User already logged in, navigating to main")
            navigateToMain()
            return
        }
        
        // Setup auto-login checkbox
        binding.checkboxAutoLogin.isChecked = preferenceManager.isAutoLoginEnabled()
        
        // Load saved username if auto-login is enabled
        if (preferenceManager.isAutoLoginEnabled()) {
            binding.editUsername.setText(preferenceManager.getSavedUsername())
        }
        
        android.util.Log.d("LoginActivity", "Setting up login button click listener")
        android.util.Log.d("LoginActivity", "Button exists: ${binding.btnLogin != null}")
        android.util.Log.d("LoginActivity", "Button isEnabled: ${binding.btnLogin.isEnabled}")
        android.util.Log.d("LoginActivity", "Button isClickable: ${binding.btnLogin.isClickable}")
        
        binding.btnLogin.setOnClickListener {
            android.util.Log.i("LoginActivity", "=== LOGIN BUTTON CLICKED ===")
            android.util.Log.i("LoginActivity", "Button click handler triggered!")
            performLogin()
        }
        
        // 차량 데이터 새로고침 버튼 클릭 리스너
        binding.btnRefreshVehicleData.setOnClickListener {
            android.util.Log.i("LoginActivity", "=== REFRESH VEHICLE DATA BUTTON CLICKED ===")
            refreshVehicleData()
        }
        
        // IME 액션 처리 - 비밀번호 입력 후 완료 버튼 클릭시 로그인 실행
        binding.editPassword.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                performLogin()
                true
            } else {
                false
            }
        }
        
        android.util.Log.d("LoginActivity", "onCreate completed")
    }
    
    private fun performLogin() {
        val username = binding.editUsername.text.toString().trim()
        val password = binding.editPassword.text.toString().trim()
        
        android.util.Log.d("LoginActivity", "performLogin called - username: $username")
        
        if (username.isEmpty() || password.isEmpty()) {
            android.util.Log.d("LoginActivity", "Empty credentials")
            Toast.makeText(this, "아이디와 비밀번호를 입력해주세요", Toast.LENGTH_SHORT).show()
            return
        }
        
        android.util.Log.d("LoginActivity", "Starting login request")
        showLoading(true)
        
        lifecycleScope.launch {
            try {
                android.util.Log.d("LoginActivity", "Making API call")
                val response = NetworkModule.apiService.login(
                    LoginRequest(username, password)
                )
                
                android.util.Log.d("LoginActivity", "API call completed - success: ${response.isSuccessful}")
                
                if (response.isSuccessful && response.body()?.success == true) {
                    val loginResponse = response.body()!!
                    
                    android.util.Log.d("LoginActivity", "Login response - token: ${loginResponse.token}, accessToken: ${loginResponse.accessToken}")
                    
                    // Check if token is available
                    val authToken = loginResponse.accessToken
                    if (authToken.isNullOrEmpty()) {
                        android.util.Log.e("LoginActivity", "Token is null or empty!")
                        showLoading(false)
                        Toast.makeText(this@LoginActivity, "로그인 토큰 오류", Toast.LENGTH_SHORT).show()
                        return@launch
                    }
                    
                    // Save user session
                    UserSession.user = loginResponse.user
                    
                    // Save user info to preferences for persistence
                    preferenceManager.saveUserInfo(loginResponse.user)
                    
                    preferenceManager.saveLoginInfo(
                        username = username,
                        token = authToken,
                        refreshToken = loginResponse.refreshToken ?: "",
                        userRole = loginResponse.user.userRole,
                        communityId = loginResponse.user.communityId ?: "",
                        autoLogin = binding.checkboxAutoLogin.isChecked
                    )
                    
                    // 권한 체크 후 새로고침 버튼 표시
                    checkAndShowRefreshButton(loginResponse.user)
                    
                    // 메인 화면으로 이동하기 전에 잠시 대기 (사용자가 버튼을 볼 수 있도록)
                    android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                        navigateToMain()
                    }, 2000) // 2초 대기
                } else {
                    showLoading(false)
                    val errorMsg = response.body()?.message ?: "로그인 실패 - Response code: ${response.code()}"
                    android.util.Log.d("LoginActivity", "Login failed: $errorMsg")
                    Toast.makeText(this@LoginActivity, errorMsg, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                showLoading(false)
                android.util.Log.e("LoginActivity", "Login exception", e)
                Toast.makeText(this@LoginActivity, 
                    "네트워크 오류: ${e.message}", 
                    Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        binding.progressBar.visibility = if (show) View.VISIBLE else View.GONE
        binding.btnLogin.isEnabled = !show
    }
    
    private fun navigateToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
    
    private fun checkAndShowRefreshButton(user: org.aptgo.vehiclemanager.models.User) {
        android.util.Log.d("LoginActivity", "Checking refresh permission for user: ${user.username}, type: ${user.user_type}, manager: ${user.is_manager}")
        
        if (user.canRefreshVehicleData()) {
            android.util.Log.d("LoginActivity", "User has refresh permission, showing button")
            binding.btnRefreshVehicleData.visibility = View.VISIBLE
            Toast.makeText(this, "차량 데이터 새로고침 권한이 부여되었습니다", Toast.LENGTH_SHORT).show()
        } else {
            android.util.Log.d("LoginActivity", "User does not have refresh permission")
            binding.btnRefreshVehicleData.visibility = View.GONE
        }
    }
    
    private fun refreshVehicleData() {
        android.util.Log.d("LoginActivity", "Starting vehicle data refresh...")
        
        // 현재 사용자 확인
        val currentUser = UserSession.user
        if (currentUser == null) {
            Toast.makeText(this, "로그인 정보가 없습니다", Toast.LENGTH_SHORT).show()
            return
        }
        
        // 권한 재확인
        if (!currentUser.canRefreshVehicleData()) {
            Toast.makeText(this, "차량 데이터 새로고침 권한이 없습니다", Toast.LENGTH_SHORT).show()
            return
        }
        
        // 토큰 확인
        val token = preferenceManager.getAuthToken()
        if (token.isNullOrEmpty()) {
            Toast.makeText(this, "인증 토큰이 없습니다. 다시 로그인해주세요", Toast.LENGTH_SHORT).show()
            return
        }
        
        // 로딩 표시
        showSyncLoading(true)
        
        lifecycleScope.launch {
            try {
                val result = VehicleDataSync.syncVehicleData(this@LoginActivity, token)
                
                showSyncLoading(false)
                
                if (result.success) {
                    Toast.makeText(
                        this@LoginActivity,
                        result.message,
                        Toast.LENGTH_LONG
                    ).show()
                    android.util.Log.d("LoginActivity", "Vehicle data sync successful: ${result.message}")
                } else {
                    Toast.makeText(
                        this@LoginActivity,
                        "동기화 실패: ${result.message}",
                        Toast.LENGTH_LONG
                    ).show()
                    android.util.Log.e("LoginActivity", "Vehicle data sync failed: ${result.message}")
                }
                
            } catch (e: Exception) {
                showSyncLoading(false)
                android.util.Log.e("LoginActivity", "Vehicle data sync exception", e)
                Toast.makeText(
                    this@LoginActivity,
                    "네트워크 오류: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    private fun showSyncLoading(show: Boolean) {
        binding.btnRefreshVehicleData.isEnabled = !show
        binding.btnRefreshVehicleData.text = if (show) "동기화 중..." else "차량 데이터 새로고침"
        if (show) {
            binding.progressBar.visibility = View.VISIBLE
        } else {
            binding.progressBar.visibility = View.GONE
        }
    }
}