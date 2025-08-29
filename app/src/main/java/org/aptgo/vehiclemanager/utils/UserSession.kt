package org.aptgo.vehiclemanager.utils

import org.aptgo.vehiclemanager.models.User

object UserSession {
    var user: User? = null
    
    fun hasPermission(permission: String): Boolean {
        return user?.permissions?.contains(permission) ?: false
    }
    
    fun isManagementAccount(): Boolean {
        return user?.userRole in listOf("super_admin", "main_account", "management_sub")
    }
    
    fun canScanVehicles(): Boolean {
        return isManagementAccount()
    }
    
    fun canViewReports(): Boolean {
        return user?.userRole in listOf("super_admin", "main_account")
    }
    
    fun canManageAccounts(): Boolean {
        return user?.userRole in listOf("super_admin", "main_account")
    }
}