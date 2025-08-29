package org.aptgo.vehiclemanager.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import org.aptgo.vehiclemanager.R
import org.aptgo.vehiclemanager.models.Vehicle
import java.text.SimpleDateFormat
import java.util.*

class VehicleCompactAdapter(
    private val onItemClick: (Vehicle) -> Unit
) : ListAdapter<Vehicle, VehicleCompactAdapter.VehicleViewHolder>(VehicleDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VehicleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_vehicle_compact, parent, false)
        return VehicleViewHolder(view, onItemClick)
    }
    
    override fun onBindViewHolder(holder: VehicleViewHolder, position: Int) {
        holder.bind(getItem(position), position)
    }
    
    class VehicleViewHolder(
        itemView: View,
        private val onItemClick: (Vehicle) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {
        
        private val textPlateNumber: TextView = itemView.findViewById(R.id.textPlateNumber)
        private val textOwnerName: TextView = itemView.findViewById(R.id.textOwnerName)
        private val textUnitNumber: TextView = itemView.findViewById(R.id.textUnitNumber)
        private val textPhoneNumber: TextView = itemView.findViewById(R.id.textPhoneNumber)
        private val textVehicleType: TextView = itemView.findViewById(R.id.textVehicleType)
        private val textStatus: TextView = itemView.findViewById(R.id.textStatus)
        
        fun bind(vehicle: Vehicle, position: Int) {
            // Plate number - keep original
            textPlateNumber.text = vehicle.plateNumber
            
            // Owner name - truncate if too long
            textOwnerName.text = vehicle.ownerName
            
            // Unit number - format compactly (동-호 format)
            val unitText = if (vehicle.unitNumber.contains("동") && vehicle.unitNumber.contains("호")) {
                val dong = vehicle.unitNumber.substringBefore("동").trim()
                val ho = vehicle.unitNumber.substringAfter("동").substringBefore("호").trim()
                "$dong-$ho"
            } else {
                vehicle.unitNumber
            }
            textUnitNumber.text = unitText
            
            // Phone number - use abbreviated format if present
            textPhoneNumber.text = when {
                !vehicle.phoneNumber.isNullOrEmpty() -> vehicle.phoneNumber
                else -> "연락처 없음"
            }
            
            // Vehicle type - use compact Korean
            textVehicleType.text = when (vehicle.vehicleType) {
                "resident" -> "입주"
                "guest" -> "방문"
                "permitted" -> "허가"
                else -> vehicle.vehicleType.take(3) // Limit to 3 chars
            }
            
            // Status - use compact Korean
            textStatus.text = when (vehicle.status) {
                "active" -> "활성"
                "inactive" -> "비활성"
                else -> vehicle.status.take(3) // Limit to 3 chars
            }
            
            // Alternate row background for better readability
            itemView.setBackgroundColor(
                if (position % 2 == 0) {
                    0xFFF9F9F9.toInt() // Light gray
                } else {
                    0xFFFFFFFF.toInt() // White
                }
            )
            
            itemView.setOnClickListener {
                onItemClick(vehicle)
            }
        }
    }
    
    class VehicleDiffCallback : DiffUtil.ItemCallback<Vehicle>() {
        override fun areItemsTheSame(oldItem: Vehicle, newItem: Vehicle): Boolean {
            return oldItem.vehicleId == newItem.vehicleId
        }
        
        override fun areContentsTheSame(oldItem: Vehicle, newItem: Vehicle): Boolean {
            return oldItem == newItem
        }
    }
}