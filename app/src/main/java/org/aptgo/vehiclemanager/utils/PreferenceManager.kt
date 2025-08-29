package org.aptgo.vehiclemanager.utils

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class PreferenceManager(context: Context) {
    
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "aptgo_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    companion object {
        private const val KEY_USERNAME = "username"
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_USER_ROLE = "user_role"
        private const val KEY_COMMUNITY_ID = "community_id"
        private const val KEY_AUTO_LOGIN = "auto_login"
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
        private const val KEY_RECENT_SEARCHES = "recent_searches"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_IS_MANAGER = "is_manager"
        private const val KEY_DONG = "dong"
        private const val KEY_HO = "ho"
        private const val KEY_PHONE = "phone"
        private const val KEY_COMMUNITY_NAME = "community_name"
    }
    
    fun saveLoginInfo(
        username: String,
        token: String,
        refreshToken: String?,
        userRole: String,
        communityId: String?,
        autoLogin: Boolean
    ) {
        sharedPreferences.edit().apply {
            putString(KEY_USERNAME, username)
            putString(KEY_AUTH_TOKEN, token)
            putString(KEY_REFRESH_TOKEN, refreshToken)
            putString(KEY_USER_ROLE, userRole)
            putString(KEY_COMMUNITY_ID, communityId)
            putBoolean(KEY_AUTO_LOGIN, autoLogin)
            putBoolean(KEY_IS_LOGGED_IN, true)
            apply()
        }
    }
    
    fun clearLoginInfo() {
        sharedPreferences.edit().apply {
            remove(KEY_AUTH_TOKEN)
            remove(KEY_REFRESH_TOKEN)
            putBoolean(KEY_IS_LOGGED_IN, false)
            apply()
        }
    }
    
    fun isLoggedIn(): Boolean {
        return sharedPreferences.getBoolean(KEY_IS_LOGGED_IN, false)
    }
    
    fun isAutoLoginEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_AUTO_LOGIN, false)
    }
    
    fun getSavedUsername(): String? {
        return sharedPreferences.getString(KEY_USERNAME, null)
    }
    
    fun getAuthToken(): String? {
        return sharedPreferences.getString(KEY_AUTH_TOKEN, null)
    }
    
    fun getRefreshToken(): String? {
        return sharedPreferences.getString(KEY_REFRESH_TOKEN, null)
    }
    
    fun getUserRole(): String? {
        return sharedPreferences.getString(KEY_USER_ROLE, null)
    }
    
    fun getCommunityId(): String? {
        return sharedPreferences.getString(KEY_COMMUNITY_ID, null)
    }
    
    fun saveRecentSearches(searches: List<String>) {
        val searchString = searches.joinToString(",")
        sharedPreferences.edit().putString(KEY_RECENT_SEARCHES, searchString).apply()
    }
    
    fun getRecentSearches(): List<String> {
        val searchString = sharedPreferences.getString(KEY_RECENT_SEARCHES, "") ?: ""
        return if (searchString.isNotEmpty()) {
            searchString.split(",")
        } else {
            emptyList()
        }
    }
    
    fun saveUserInfo(user: org.aptgo.vehiclemanager.models.User) {
        sharedPreferences.edit().apply {
            putInt(KEY_USER_ID, user.id)
            putString(KEY_USERNAME, user.username)
            putString(KEY_USER_ROLE, user.user_type)
            putBoolean(KEY_IS_MANAGER, user.is_manager)
            putString(KEY_DONG, user.dong)
            putString(KEY_HO, user.ho)
            putString(KEY_PHONE, user.phone)
            putString(KEY_COMMUNITY_ID, user.communityId)
            putString(KEY_COMMUNITY_NAME, user.communityName)
            apply()
        }
    }
    
    fun getSavedUser(): org.aptgo.vehiclemanager.models.User? {
        val username = sharedPreferences.getString(KEY_USERNAME, null) ?: return null
        val userRole = sharedPreferences.getString(KEY_USER_ROLE, null) ?: return null
        
        return org.aptgo.vehiclemanager.models.User(
            id = sharedPreferences.getInt(KEY_USER_ID, 0),
            username = username,
            user_type = userRole,
            is_manager = sharedPreferences.getBoolean(KEY_IS_MANAGER, false),
            dong = sharedPreferences.getString(KEY_DONG, null),
            ho = sharedPreferences.getString(KEY_HO, null),
            phone = sharedPreferences.getString(KEY_PHONE, null),
            parent_account = null,
            communityId = sharedPreferences.getString(KEY_COMMUNITY_ID, null),
            communityName = sharedPreferences.getString(KEY_COMMUNITY_NAME, null)
        )
    }
}