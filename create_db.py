import sqlite3

def create_db():
    conn = sqlite3.connect('companies.db')
    cursor = conn.cursor()
    create_jobs = '''CREATE TABLE IF NOT EXISTS jobs (
        ID INTEGER PRIMARY KEY NOT NULL, company TEXT NOT NULL, job TEXT NOT NULL
    )'''
    cursor.execute(create_jobs)
    create_career_pages = '''CREATE TABLE IF NOT EXISTS career_pages (
        ID INTEGER PRIMARY KEY NOT NULL, company TEXT UNIQUE NOT NULL, size INTEGER NOT NULL
    )'''
    cursor.execute(create_career_pages)