package org.aptgo.vehiclemanager.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "scan_history")
data class ScanHistory(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val plateNumber: String,
    val scanType: String, // "auto" or "manual"
    val scanDate: Date,
    val isRegistered: Boolean,
    val vehicleId: String?,
    val location: String?,
    val actionTaken: String?,
    val photoPath: String?,
    val notes: String?,
    val userId: String,
    val synced: Boolean = false
)