import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/buyer_provider.dart';

/// Returns Index Screen
class ReturnsIndexScreen extends StatefulWidget {
  const ReturnsIndexScreen({super.key});

  @override
  State<ReturnsIndexScreen> createState() => _ReturnsIndexScreenState();
}

class _ReturnsIndexScreenState extends State<ReturnsIndexScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BuyerProvider>().fetchReturns();
    });
  }

  @override
  Widget build(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Returns & Refunds'),
        elevation: 0,
        backgroundColor: Colors.purple.shade600,
      ),
      body: buyerProvider.isLoading && buyerProvider.returns.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : buyerProvider.returns.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.undo, size: 80, color: Colors.grey.shade300),
                      const SizedBox(height: 16),
                      const Text(
                        'No return requests',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'You can request a return for completed orders',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  child: Column(
                    children: [
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        padding: const EdgeInsets.all(12),
                        itemCount: buyerProvider.returns.length,
                        itemBuilder: (context, index) {
                          final returnRequest = buyerProvider.returns[index];
                          return _buildReturnCard(
                              context, returnRequest, buyerProvider);
                        },
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildReturnCard(
    BuildContext context,
    dynamic returnRequest,
    BuyerProvider buyerProvider,
  ) {
    final status = returnRequest.status?.toLowerCase() ?? 'submitted';
    final isApproved = status == 'approved';
    final isRejected = status == 'rejected';
    final isPending = status == 'submitted' || status == 'pending';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => buyerProvider.selectReturn(returnRequest.id),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with status
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Return #${returnRequest.id}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Order #${returnRequest.orderId}',
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: _getStatusColor(status).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _getStatusColor(status),
                        width: 1.5,
                      ),
                    ),
                    child: Text(
                      _getStatusLabel(status),
                      style: TextStyle(
                        color: _getStatusColor(status),
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const Divider(height: 24),
              // Details
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildDetailRow(
                    'Reason',
                    returnRequest.reason ?? 'No reason provided',
                  ),
                  const SizedBox(height: 8),
                  _buildDetailRow(
                    'Requested',
                    returnRequest.requestDate.toString().split(' ')[0],
                  ),
                  if (returnRequest.mediaUrls.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _buildDetailRow(
                      'Evidence',
                      '${returnRequest.mediaUrls.length} file(s) attached',
                      valueColor: Colors.purple.shade600,
                    ),
                  ],
                ],
              ),
              // Status messages
              if (isApproved) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.check_circle,
                        color: Colors.green.shade700,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Your return request was approved. The item is now refunded.',
                          style: TextStyle(
                            color: Colors.green.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              if (isRejected) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.cancel,
                        color: Colors.red.shade700,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Your return request was rejected by the seller.',
                          style: TextStyle(
                            color: Colors.red.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              if (isPending) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.orange.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.schedule,
                        color: Colors.orange.shade700,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Waiting for seller to review your request.',
                          style: TextStyle(
                            color: Colors.orange.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, {Color? valueColor}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 13,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: TextStyle(
              color: valueColor ?? Colors.black87,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  String _getStatusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'submitted':
      case 'pending':
        return 'PENDING';
      case 'approved':
        return 'APPROVED';
      case 'rejected':
        return 'REJECTED';
      default:
        return status.toUpperCase();
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'approved':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      case 'processing':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
}

/// Return Form Screen
class ReturnFormScreen extends StatefulWidget {
  final int orderId;

  const ReturnFormScreen({super.key, required this.orderId});

  @override
  State<ReturnFormScreen> createState() => _ReturnFormScreenState();
}

class _ReturnFormScreenState extends State<ReturnFormScreen> {
  late TextEditingController _reasonController;
  late TextEditingController _descriptionController;
  String? _selectedReason;
  final List<String> _reasons = [
    'Defective/Damaged',
    'Not as Described',
    'Wrong Item',
    'Changed Mind',
    'Size Issue',
    'Quality Issue',
    'Other',
  ];

  @override
  void initState() {
    super.initState();
    _reasonController = TextEditingController();
    _descriptionController = TextEditingController();
  }

  @override
  void dispose() {
    _reasonController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _submitReturn(BuyerProvider buyerProvider) async {
    if (_selectedReason == null || _descriptionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all required fields')),
      );
      return;
    }

    final success = await buyerProvider.createReturn(
      orderId: widget.orderId,
      reason: _selectedReason!,
      description: _descriptionController.text,
    );

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Return request submitted successfully')),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(
                  buyerProvider.errorMessage ?? 'Failed to submit return')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final buyerProvider = context.watch<BuyerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Request Return'),
        elevation: 0,
        backgroundColor: Colors.purple.shade600,
      ),
      body: buyerProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (buyerProvider.errorMessage != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade100,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          buyerProvider.errorMessage!,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    const SizedBox(height: 16),
                    // Order ID Display
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Row(
                          children: [
                            const Icon(Icons.shopping_bag,
                                color: Colors.purple),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Order Number',
                                    style: TextStyle(color: Colors.grey)),
                                Text(
                                  '#${widget.orderId}',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    // Return Reason
                    const Text(
                      'Return Reason *',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      initialValue: _selectedReason,
                      items: _reasons
                          .map((reason) => DropdownMenuItem(
                                value: reason,
                                child: Text(reason),
                              ))
                          .toList(),
                      onChanged: (value) =>
                          setState(() => _selectedReason = value),
                      decoration: InputDecoration(
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8)),
                        hintText: 'Choose a reason',
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Description
                    const Text(
                      'Description *',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _descriptionController,
                      maxLines: 4,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8)),
                        hintText: 'Describe the issue in detail...',
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Media Section
                    const Text(
                      'Attach Photos or Videos (Optional)',
                      style:
                          TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border:
                            Border.all(color: Colors.grey.shade300, width: 2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.cloud_upload_outlined,
                              size: 48, color: Colors.grey.shade400),
                          const SizedBox(height: 12),
                          const Text('Tap to upload media files'),
                          const SizedBox(height: 8),
                          Text(
                            'Max 5 files - JPG, PNG, or MP4',
                            style: TextStyle(
                                color: Colors.grey.shade600, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Action Buttons
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: buyerProvider.isLoading
                            ? null
                            : () => _submitReturn(buyerProvider),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.purple.shade600,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: buyerProvider.isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white),
                                ),
                              )
                            : const Text(
                                'Submit Return Request',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('Cancel'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
