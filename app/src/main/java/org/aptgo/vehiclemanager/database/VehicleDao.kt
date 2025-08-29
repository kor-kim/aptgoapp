package org.aptgo.vehiclemanager.database

import androidx.room.*
import kotlinx.coroutines.flow.Flow
import org.aptgo.vehiclemanager.models.Vehicle

@Dao
interface VehicleDao {
    @Query("SELECT * FROM vehicles WHERE plateNumber = :plateNumber LIMIT 1")
    suspend fun getVehicleByPlateNumber(plateNumber: String): Vehicle?

    @Query("SELECT * FROM vehicles WHERE plateNumber LIKE :query")
    suspend fun searchVehicles(query: String): List<Vehicle>

    @Query("SELECT * FROM vehicles")
    fun getAllVehicles(): Flow<List<Vehicle>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertVehicle(vehicle: Vehicle)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertVehicles(vehicles: List<Vehicle>)

    @Update
    suspend fun updateVehicle(vehicle: Vehicle)

    @Delete
    suspend fun deleteVehicle(vehicle: Vehicle)

    @Query("DELETE FROM vehicles")
    suspend fun deleteAllVehicles()

    @Query("SELECT COUNT(*) FROM vehicles")
    suspend fun getVehicleCount(): Int
}