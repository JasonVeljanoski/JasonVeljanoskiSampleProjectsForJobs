# Run migrations
alembic upgrade head
# Create initial data in DB
python /app/app/db/init_db.py