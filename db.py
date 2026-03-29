import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
	return psycopg2.connect(DATABASE_URL)

def create_tables():
	conn = get_connection()
	cursor = conn.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			telegram_id BIGINT UNIQUE,
			name TEXT,
			weight REAL,
			hright REAL
		)
	''')

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS reminders (
			id SERIAL PRIMARY KEY,
			telegram_id BIGINT,
			time TEXT
		)
	''')

	conn.commit()
	cursor.close()
	conn.close()