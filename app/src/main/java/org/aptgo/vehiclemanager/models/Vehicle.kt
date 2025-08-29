package org.aptgo.vehiclemanager.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.Date

@Entity(
    tableName = "vehicles",
    indices = [Index(value = ["plateNumber"], unique = false)]
)
data class Vehicle(
    @PrimaryKey
    val vehicleId: String,
    val plateNumber: String,
    val ownerName: String,
    val unitNumber: String,
    val phoneNumber: String?,
    val registrationDate: Date,
    val status: String, // active, inactive
    val vehicleType: String, // resident, guest, permitted
    val memo: String?,
    val lastUpdated: Date,
    val communityId: String?
)