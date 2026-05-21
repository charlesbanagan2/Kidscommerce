"""
Test script to check rider earnings data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, WalletTransaction, User
from datetime import datetime, timedelta

def main():
    print("\n" + "="*70)
    print("  💰 RIDER EARNINGS TEST")
    print("="*70)
    
    with app.app_context():
        # Check specific rider ID 28
        rider = User.query.get(28)
        if not rider:
            print("❌ Rider ID 28 not found in database")
            return
        
        print(f"\n👤 Testing rider: {rider.first_name} {rider.last_name} (ID: {rider.id})")
        print(f"   Role: {rider.role}")
        
        # Get all wallet transactions for this rider
        all_transactions = WalletTransaction.query.filter_by(
            user_id=rider.id,
            type='credit'
        ).order_by(WalletTransaction.created_at.desc()).all()
        
        print(f"\n📊 Total wallet transactions: {len(all_transactions)}")
        
        if not all_transactions:
            print("⚠️  No wallet transactions found for this rider")
            print("\nℹ️  Wallet transactions are created when:")
            print("   1. Order is completed by buyer")
            print("   2. Rider delivery fee is released")
            return
        
        # Calculate earnings by period (using Philippine Time UTC+8)
        from datetime import timezone as dt_timezone
        ph_tz = dt_timezone(timedelta(hours=8))
        now = datetime.now(ph_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        print(f"\n🕐 Current Time (PH): {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
        print(f"   Today starts at: {today_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Week starts at: {week_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Month starts at: {month_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Count NULL created_at values
        null_count = sum(1 for t in all_transactions if t.created_at is None)
        if null_count > 0:
            print(f"\n⚠️  WARNING: {null_count} transactions have NULL created_at!")
            print("   These transactions will be excluded from period calculations.")
        
        total_earnings = sum(t.amount for t in all_transactions)
        
        # Handle timezone-aware vs naive datetime comparison
        def safe_compare(dt, threshold):
            if dt is None:
                return False
            # Convert both to timezone-aware for comparison
            if dt.tzinfo is None:
                # Assume UTC if no timezone
                dt = dt.replace(tzinfo=dt_timezone.utc)
            if threshold.tzinfo is None:
                threshold = threshold.replace(tzinfo=ph_tz)
            return dt >= threshold
        
        today_earnings = sum(t.amount for t in all_transactions if safe_compare(t.created_at, today_start))
        week_earnings = sum(t.amount for t in all_transactions if safe_compare(t.created_at, week_start))
        month_earnings = sum(t.amount for t in all_transactions if safe_compare(t.created_at, month_start))
        
        print(f"\n💵 Earnings Breakdown:")
        print(f"   • Total: ₱{total_earnings:.2f}")
        print(f"   • Today: ₱{today_earnings:.2f}")
        print(f"   • This Week: ₱{week_earnings:.2f}")
        print(f"   • This Month: ₱{month_earnings:.2f}")
        
        # Show ALL transactions with details
        print(f"\n📝 All Transactions ({len(all_transactions)}):")
        
        for i, t in enumerate(all_transactions, 1):
            # Handle NULL created_at
            if t.created_at is None:
                age_str = "NULL DATE"
                period_str = "⚠️ NULL - EXCLUDED FROM CALCULATIONS"
            else:
                # Convert to PH timezone for display
                created_dt = t.created_at
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=dt_timezone.utc)
                created_ph = created_dt.astimezone(ph_tz)
                
                age = now - created_ph
                if age.days == 0:
                    if age.seconds < 3600:
                        age_str = f"{age.seconds // 60}m ago"
                    else:
                        age_str = f"{age.seconds // 3600}h ago"
                else:
                    age_str = f"{age.days}d ago"
                
                # Check which period this belongs to
                periods = []
                if created_ph >= today_start:
                    periods.append("TODAY")
                if created_ph >= week_start:
                    periods.append("WEEK")
                if created_ph >= month_start:
                    periods.append("MONTH")
                
                period_str = ", ".join(periods) if periods else "OLDER"
            
            print(f"\n   {i}. ₱{t.amount:.2f} - {t.source} - {age_str}")
            print(f"      Order #{t.order_id}")
            if t.created_at:
                created_display = t.created_at
                if created_display.tzinfo is None:
                    created_display = created_display.replace(tzinfo=dt_timezone.utc)
                created_ph_display = created_display.astimezone(ph_tz)
                print(f"      Created: {created_ph_display.strftime('%Y-%m-%d %H:%M:%S')} (PH Time)")
            else:
                print(f"      Created: NULL ⚠️")
            print(f"      Period: {period_str}")
        
        # Summary
        print("\n" + "="*70)
        print("✅ TEST COMPLETE")
        print("="*70)
        
        if today_earnings == 0:
            print("\n⚠️  No earnings today - all transactions are from previous days")
        if week_earnings == 0:
            print("⚠️  No earnings this week - all transactions are older than 7 days")

if __name__ == '__main__':
    main()
