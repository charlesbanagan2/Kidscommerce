from sqlalchemy import create_engine, text

# Supabase DB URL from backend/.env
DB_URL = "postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DB_URL)
with engine.connect() as conn:
    conn.execute(text("SELECT setval(pg_get_serial_sequence('coupon','id'), (SELECT COALESCE(MAX(id),0) FROM coupon) + 1);"))
    print('coupon sequence resynced to MAX(id)+1')
