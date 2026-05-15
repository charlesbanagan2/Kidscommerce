from app import app, db, User, bcrypt

with app.app_context():
    admin = User.query.filter_by(email='admin@kidscommerce.com').first()
    if admin:
        admin.password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()
        print('Admin password updated to bcrypt hash')
    else:
        print('Admin not found')
