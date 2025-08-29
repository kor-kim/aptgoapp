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

class VehicleSearchAdapter(
    private val onItemClick: (Vehicle) -> Unit
) : ListAdapter<Vehicle, VehicleSearchAdapter.VehicleViewHolder>(VehicleDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VehicleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_vehicle_search, parent, false)
        return VehicleViewHolder(view, onItemClick)
    }
    
    override fun onBindViewHolder(holder: VehicleViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    fun clearResults() {
        submitList(emptyList())
    }
    
    class VehicleViewHolder(
        itemView: View,
        private val onItemClick: (Vehicle) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {
        
        private val textPlateNumber: TextView = itemView.findViewById(R.id.textPlateNumber)
        private val textOwnerName: TextView = itemView.findViewById(R.id.textOwnerName)
        private val textUnitNumber: TextView = itemView.findViewById(R.id.textUnitNumber)
        private val textVehicleType: TextView = itemView.findViewById(R.id.textVehicleType)
        
        fun bind(vehicle: Vehicle) {
            textPlateNumber.text = vehicle.plateNumber
            textOwnerName.text = vehicle.ownerName
            textUnitNumber.text = vehicle.unitNumber
            textVehicleType.text = when (vehicle.vehicleType) {
                "resident" -> "입주민"
                "guest" -> "방문"
                "permitted" -> "허가"
                else -> vehicle.vehicleType
            }
            
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