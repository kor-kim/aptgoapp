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

class VehicleDataAdapter(
    private val onItemClick: (Vehicle) -> Unit
) : ListAdapter<Vehicle, VehicleDataAdapter.VehicleViewHolder>(VehicleDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VehicleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_vehicle_data, parent, false)
        return VehicleViewHolder(view, onItemClick)
    }
    
    override fun onBindViewHolder(holder: VehicleViewHolder, position: Int) {
        holder.bind(getItem(position))
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
        private val textRegistrationDate: TextView = itemView.findViewById(R.id.textRegistrationDate)
        
        fun bind(vehicle: Vehicle) {
            textPlateNumber.text = vehicle.plateNumber
            textOwnerName.text = vehicle.ownerName
            textUnitNumber.text = vehicle.unitNumber
            
            // 전화번호가 있으면 표시, 없으면 "-"
            textPhoneNumber.text = if (!vehicle.phoneNumber.isNullOrEmpty()) {
                vehicle.phoneNumber
            } else {
                "연락처 없음"
            }
            
            // 차량 타입을 한국어로 변환
            textVehicleType.text = when (vehicle.vehicleType) {
                "resident" -> "입주민"
                "guest" -> "방문"
                "permitted" -> "허가"
                else -> vehicle.vehicleType
            }
            
            // 상태를 한국어로 변환
            textStatus.text = when (vehicle.status) {
                "active" -> "활성"
                "inactive" -> "비활성"
                else -> vehicle.status
            }
            
            // 등록일자 포맷팅
            val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            textRegistrationDate.text = "등록일: ${dateFormat.format(vehicle.registrationDate)}"
            
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