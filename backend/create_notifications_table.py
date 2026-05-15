"""
Database Migration Script
Run this to create the notifications table
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/kids_ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create notifications table
def create_notifications_table():
    """Create notifications table if it doesn't exist"""
    
    sql = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_role VARCHAR(20) NOT NULL,
        title VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        notification_type VARCHAR(50) NOT NULL,
        order_id INTEGER,
        action_url VARCHAR(500),
        is_read BOOLEAN DEFAULT 0,
        is_pushed BOOLEAN DEFAULT 0,
        metadata JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, user_role);
    CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read);
    CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);
    """
    
    with app.app_context():
        db.session.execute(sql)
        db.session.commit()
        print("✅ Notifications table created successfully!")

if __name__ == '__main__':
    create_notifications_table()
