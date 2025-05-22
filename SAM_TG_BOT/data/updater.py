import requests
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import url_topics, url_teachers

os.remove('base.db') if os.path.exists('base.db') else None

conn = sqlite3.connect('base.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        telegram_id INTEGER
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_topics (
        teacher_id INTEGER,
        topic_id INTEGER,
        PRIMARY KEY (teacher_id, topic_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers (id),
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
""")

conn.commit()

response = requests.get(url=url_topics)
topics_data = response.json()

for item in topics_data:
    topic = item.get('topic_name')
    if topic:
        try:
            cursor.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic,))
        except sqlite3.IntegrityError:
            pass

conn.commit()

response = requests.get(url=url_teachers)
teachers_data = response.json()

for item in teachers_data:
    id_ = item.get('id')
    full_name = item.get('full_name')
    telegram_id = item.get('telegram_id')
    topic_objs = item.get('topics')

    if id_ is not None and full_name and telegram_id is not None:
        cursor.execute(
            "INSERT OR IGNORE INTO teachers (id, full_name, telegram_id) VALUES (?, ?, ?)",
            (id_, full_name, telegram_id)
        )

        if topic_objs and isinstance(topic_objs, list):
            for topic_dict in topic_objs:
                topic_name = topic_dict.get('topic_name')
                if topic_name:
                    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
                    result = cursor.fetchone()
                    if result:
                        topic_id = result[0]
                    else:
                        cursor.execute("INSERT INTO topics (name) VALUES (?)", (topic_name,))
                        topic_id = cursor.lastrowid

                    cursor.execute(
                        "INSERT OR IGNORE INTO teacher_topics (teacher_id, topic_id) VALUES (?, ?)",
                        (id_, topic_id)
                    )

conn.commit()
conn.close()
