from app import app, db
from sqlalchemy import text

app.app_context().push()

# Test query for seller with store logo
result = db.session.execute(text("""
    SELECT u.id, u.first_name, u.last_name, u.role, u.profile_picture,
           sa.store_logo, sa.store_name
    FROM "user" u
    LEFT JOIN seller_application sa ON u.id = sa.user_id AND sa.status = 'approved'
    WHERE u.id = 16
"""))

row = result.fetchone()
if row:
    print(f'User ID: {row[0]}')
    print(f'Name: {row[1]} {row[2]}')
    print(f'Role: {row[3]}')
    print(f'Profile Picture: {row[4]}')
    print(f'Store Logo: {row[5]}')
    print(f'Store Name: {row[6]}')
    print()
    print(f'Will use: {row[5] if row[5] else row[4]}')
    print(f'Display name: {row[6] if row[6] else f"{row[1]} {row[2]}"}')
else:
    print('No user found')
