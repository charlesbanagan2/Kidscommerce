from app import app, db, User
import bcrypt

with app.app_context():
    email = 'malakaslang53@gmail.com'
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Hash the password using bcrypt
        password = 'Buyer@1234'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update the user's password
        user.password = hashed_password
        db.session.commit()
        
        print(f'Password updated for user: {email}')
        print(f'New hash: {hashed_password[:50]}...')
    else:
        print(f'User not found with email: {email}')
