package org.aptgo.vehiclemanager.activities

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import kotlinx.coroutines.launch
import org.aptgo.vehiclemanager.adapters.VehicleSearchAdapter
import org.aptgo.vehiclemanager.database.AppDatabase
import org.aptgo.vehiclemanager.databinding.ActivityManualSearchBinding
import org.aptgo.vehiclemanager.models.ScanHistory
import org.aptgo.vehiclemanager.models.Vehicle
import org.aptgo.vehiclemanager.utils.PreferenceManager
import org.aptgo.vehiclemanager.views.KoreanPlateKeypadView
import java.util.Date

class ManualSearchActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityManualSearchBinding
    private lateinit var database: AppDatabase
    private lateinit var preferenceManager: PreferenceManager
    private lateinit var searchAdapter: VehicleSearchAdapter
    
    private val koreanChars = arrayOf(
        "가", "나", "다", "라", "마", "거", "너", "더", "러", "머",
        "버", "서", "어", "저", "고", "노", "도", "로", "모", "보",
        "소", "오", "조", "구", "누", "두", "루", "무", "부", "수",
        "우", "주", "아", "바", "사", "자", "허", "배", "호", "하"
    )
    
    private var currentInputMode = InputMode.NUMBERS
    private val recentSearches = mutableListOf<String>()
    
    enum class InputMode {
        NUMBERS, KOREAN
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityManualSearchBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        database = AppDatabase.getDatabase(this)
        preferenceManager = PreferenceManager(this)
        
        setupToolbar()
        setupSearchInput()
        setupKeypad()
        setupRecyclerView()
        loadRecentSearches()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "수동 차량 검색"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupSearchInput() {
        binding.editPlateNumber.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                val query = s.toString().trim()
                if (query.length >= 2) {
                    performSearch(query)
                } else {
                    searchAdapter.clearResults()
                    showRecentSearches()
                }
            }
            
            override fun afterTextChanged(s: Editable?) {}
        })
        
        binding.btnClear.setOnClickListener {
            binding.editPlateNumber.text.clear()
            searchAdapter.clearResults()
            showRecentSearches()
        }
        
        binding.btnSearch.setOnClickListener {
            val query = binding.editPlateNumber.text.toString().trim()
            if (query.isNotEmpty()) {
                performFullSearch(query)
            }
        }
        
        binding.btnCameraMode.setOnClickListener {
            startActivity(Intent(this, CameraScanActivity::class.java))
            finish()
        }
    }
    
    private fun setupKeypad() {
        // Number buttons setup
        val numberButtons = listOf(
            binding.btn1, binding.btn2, binding.btn3,
            binding.btn4, binding.btn5, binding.btn6,
            binding.btn7, binding.btn8, binding.btn9,
            binding.btn0
        )
        
        numberButtons.forEachIndexed { index, button ->
            val number = if (index == 9) "0" else (index + 1).toString()
            button.text = number
            button.setOnClickListener {
                appendToInput(number)
            }
        }
        
        // Korean character grid
        setupKoreanGrid()
        
        // Mode switch button
        binding.btnSwitchMode.setOnClickListener {
            toggleInputMode()
        }
        
        // Backspace button
        binding.btnBackspace.setOnClickListener {
            val currentText = binding.editPlateNumber.text.toString()
            if (currentText.isNotEmpty()) {
                binding.editPlateNumber.setText(currentText.dropLast(1))
                binding.editPlateNumber.setSelection(binding.editPlateNumber.text.length)
            }
        }
        
        // Wildcard button
        binding.btnWildcard.setOnClickListener {
            appendToInput("*")
        }
    }
    
    private fun setupKoreanGrid() {
        binding.koreanGrid.removeAllViews()
        
        koreanChars.forEach { char ->
            val button = android.widget.Button(this).apply {
                text = char
                textSize = 16f
                setOnClickListener {
                    appendToInput(char)
                }
            }
            binding.koreanGrid.addView(button)
        }
    }
    
    private fun toggleInputMode() {
        currentInputMode = when (currentInputMode) {
            InputMode.NUMBERS -> InputMode.KOREAN
            InputMode.KOREAN -> InputMode.NUMBERS
        }
        
        when (currentInputMode) {
            InputMode.NUMBERS -> {
                binding.numberKeypad.visibility = View.VISIBLE
                binding.koreanKeypad.visibility = View.GONE
                binding.btnSwitchMode.text = "한글"
            }
            InputMode.KOREAN -> {
                binding.numberKeypad.visibility = View.GONE
                binding.koreanKeypad.visibility = View.VISIBLE
                binding.btnSwitchMode.text = "숫자"
            }
        }
    }
    
    private fun appendToInput(text: String) {
        val currentText = binding.editPlateNumber.text.toString()
        binding.editPlateNumber.setText(currentText + text)
        binding.editPlateNumber.setSelection(binding.editPlateNumber.text.length)
    }
    
    private fun setupRecyclerView() {
        searchAdapter = VehicleSearchAdapter { vehicle ->
            showVehicleDetail(vehicle)
        }
        
        binding.recyclerSearchResults.apply {
            layoutManager = LinearLayoutManager(this@ManualSearchActivity)
            adapter = searchAdapter
        }
    }
    
    private fun performSearch(query: String) {
        lifecycleScope.launch {
            val wildcardQuery = query.replace("*", "%")
            val results = if (wildcardQuery.contains("%")) {
                database.vehicleDao().searchVehicles(wildcardQuery)
            } else {
                database.vehicleDao().searchVehicles("%$wildcardQuery%")
            }
            
            runOnUiThread {
                if (results.isNotEmpty()) {
                    binding.textNoResults.visibility = View.GONE
                    searchAdapter.submitList(results)
                } else {
                    binding.textNoResults.visibility = View.VISIBLE
                    binding.textNoResults.text = "검색 결과가 없습니다"
                    searchAdapter.clearResults()
                }
            }
        }
    }
    
    private fun performFullSearch(query: String) {
        // Add to recent searches
        if (!recentSearches.contains(query)) {
            recentSearches.add(0, query)
            if (recentSearches.size > 10) {
                recentSearches.removeLast()
            }
            saveRecentSearches()
        }
        
        performSearch(query)
        
        // Save manual search history
        lifecycleScope.launch {
            val vehicle = database.vehicleDao().getVehicleByPlateNumber(query)
            val scanHistory = ScanHistory(
                plateNumber = query,
                scanType = "manual",
                scanDate = Date(),
                isRegistered = vehicle != null,
                vehicleId = vehicle?.vehicleId,
                location = "수동 검색",
                actionTaken = null,
                photoPath = null,
                notes = null,
                userId = preferenceManager.getSavedUsername() ?: "",
                synced = false
            )
            
            database.scanHistoryDao().insertScanHistory(scanHistory)
        }
    }
    
    private fun showVehicleDetail(vehicle: Vehicle) {
        val intent = Intent(this, VehicleDetailActivity::class.java).apply {
            putExtra("vehicle_id", vehicle.vehicleId)
            putExtra("plate_number", vehicle.plateNumber)
            putExtra("owner_name", vehicle.ownerName)
            putExtra("unit_number", vehicle.unitNumber)
            putExtra("phone_number", vehicle.phoneNumber)
            putExtra("vehicle_type", vehicle.vehicleType)
        }
        startActivity(intent)
    }
    
    private fun loadRecentSearches() {
        val savedSearches = preferenceManager.getRecentSearches()
        if (savedSearches.isNotEmpty()) {
            recentSearches.clear()
            recentSearches.addAll(savedSearches)
            showRecentSearches()
        }
    }
    
    private fun saveRecentSearches() {
        preferenceManager.saveRecentSearches(recentSearches)
    }
    
    private fun showRecentSearches() {
        if (recentSearches.isNotEmpty() && binding.editPlateNumber.text.isEmpty()) {
            binding.textNoResults.visibility = View.VISIBLE
            binding.textNoResults.text = "최근 검색"
            
            val recentVehicles = mutableListOf<Vehicle>()
            lifecycleScope.launch {
                recentSearches.forEach { plateNumber ->
                    database.vehicleDao().getVehicleByPlateNumber(plateNumber)?.let {
                        recentVehicles.add(it)
                    }
                }
                
                runOnUiThread {
                    if (recentVehicles.isNotEmpty()) {
                        searchAdapter.submitList(recentVehicles)
                    }
                }
            }
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}