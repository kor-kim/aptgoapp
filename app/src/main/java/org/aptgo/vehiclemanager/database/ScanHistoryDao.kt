package org.aptgo.vehiclemanager.database

import androidx.room.*
import kotlinx.coroutines.flow.Flow
import org.aptgo.vehiclemanager.models.ScanHistory
import java.util.Date

@Dao
interface ScanHistoryDao {
    @Insert
    suspend fun insertScanHistory(scanHistory: ScanHistory): Long

    @Query("SELECT * FROM scan_history ORDER BY scanDate DESC")
    fun getAllScanHistory(): Flow<List<ScanHistory>>

    @Query("SELECT * FROM scan_history WHERE scanDate BETWEEN :startDate AND :endDate ORDER BY scanDate DESC")
    suspend fun getScanHistoryByDateRange(startDate: Date, endDate: Date): List<ScanHistory>

    @Query("SELECT * FROM scan_history WHERE scanType = :scanType ORDER BY scanDate DESC")
    suspend fun getScanHistoryByType(scanType: String): List<ScanHistory>

    @Query("SELECT * FROM scan_history WHERE synced = 0")
    suspend fun getUnsyncedHistory(): List<ScanHistory>

    @Query("UPDATE scan_history SET synced = 1 WHERE id IN (:ids)")
    suspend fun markAsSynced(ids: List<Long>)

    @Query("SELECT COUNT(*) FROM scan_history WHERE DATE(scanDate/1000, 'unixepoch') = DATE('now')")
    suspend fun getTodayScansCount(): Int

    @Query("SELECT COUNT(*) FROM scan_history WHERE scanType = :scanType AND DATE(scanDate/1000, 'unixepoch') = DATE('now')")
    suspend fun getTodayScansCountByType(scanType: String): Int
}