import sqlite3
from database import DATABASE_PATH

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
    ALTER TABLE notifications
    ADD COLUMN next_send_at TEXT
""")

connection.commit()
connection.close()

print("Coluna next_send_at adicionada com sucesso!")