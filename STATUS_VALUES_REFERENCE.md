# Status Values Reference Guide

## Product Status Values
Products use these status values:
- `approved` - Product is approved by admin and visible to buyers ✅
- `pending` - Product waiting for admin approval
- `rejected` - Product rejected by admin
- `inactive` - Product deactivated by seller

**Important:** Cart and checkout endpoints should check for `status == 'approved'`

### Example:
```python
product = get_data_by_id('product', product_id)
if not product or product.get('status') != 'approved':  # ✅ Correct
    return jsonify({'error': 'Product not found'}), 404
```

## User Status Values
Users (buyers, sellers, riders, admin) use these status values:
- `active` - User account is active and can use the system ✅
- `pending` - User waiting for admin approval (especially riders)
- `suspended` - User account suspended by admin
- `rejected` - User account rejected by admin

**Important:** Authentication and user validation should check for `status == 'active'`

### Example:
```python
user = get_data_by_id('user', user_id)
if not user or user.get('status') != 'active':  # ✅ Correct
    return jsonify({'error': 'User not found or inactive'}), 401
```

## Category Status Values
Categories use:
- `active` - Category is active and visible
- `inactive` - Category is hidden

## Summary Table

| Entity | Active Status | Pending Status | Rejected Status | Inactive Status |
|--------|--------------|----------------|-----------------|-----------------|
| **Product** | `approved` ✅ | `pending` | `rejected` | `inactive` |
| **User** | `active` ✅ | `pending` | `rejected` | `suspended` |
| **Category** | `active` ✅ | - | - | `inactive` |

## Common Mistakes to Avoid

### ❌ Wrong:
```python
# Checking product with 'active'
if product.get('status') != 'active':  # Wrong!
```

### ✅ Correct:
```python
# Checking product with 'approved'
if product.get('status') != 'approved':  # Correct!
```

---
**Last Updated:** May 20, 2026
