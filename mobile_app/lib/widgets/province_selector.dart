import 'package:flutter/material.dart';
import '../services/delivery_fee_service.dart';

class ProvinceSelector extends StatelessWidget {
  final String? selectedProvince;
  final ValueChanged<String?> onChanged;

  const ProvinceSelector({
    super.key,
    required this.selectedProvince,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final provinces = DeliveryFeeService.getAllProvinces();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: selectedProvince,
          hint: const Text('Select Province'),
          isExpanded: true,
          icon: const Icon(Icons.arrow_drop_down),
          items: provinces.map((province) {
            final fee = DeliveryFeeService.calculateDeliveryFee(province);
            return DropdownMenuItem(
              value: province,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      province,
                      style: const TextStyle(fontSize: 14),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Text(
                    '₱${fee.toStringAsFixed(0)}/item',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}
