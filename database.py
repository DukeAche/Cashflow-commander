import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import bcrypt

class CashflowDatabase:
    def __init__(self, db_path="cashflow.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with transactions table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('Income', 'Expense')),
                    category TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if username column exists in transactions (migration)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'username' not in columns:
                conn.execute("ALTER TABLE transactions ADD COLUMN username TEXT")
                conn.execute("UPDATE transactions SET username = 'admin'")
            
            # Create categories table for consistency
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('Income', 'Expense'))
                )
            ''')
            
            # Insert default categories if not exists
            default_categories = [
                ('Sales', 'Income'), ('Services', 'Income'), ('Other Income', 'Income'),
                ('Rent', 'Expense'), ('Supplies', 'Expense'), ('Utilities', 'Expense'),
                ('Marketing', 'Expense'), ('Insurance', 'Expense'), ('Other Expense', 'Expense')
            ]
            
            for name, type in default_categories:
                conn.execute('''
                    INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)
                ''', (name, type))
            # Create users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash BLOB NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create login logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS login_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL CHECK (status IN ('Success', 'Failure'))
                )
            ''')
            
            # Check if admin exists, if not create default admin
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM users WHERE role='admin'")
            if cursor.fetchone()[0] == 0:
                # Create default admin: admin / admin123
                password = b"admin123"
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", hashed, "admin")
                )
    def add_transaction(self, username, date, type, category, amount, description):
        """Add a new transaction"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO transactions (username, date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, date, type, category, amount, description))
    
    def get_all_transactions(self, username):
        """Get all transactions for a user as a DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT id, date, type, category, amount, description, created_at
                FROM transactions
                WHERE username = ?
                ORDER BY date DESC, id DESC
            ''', conn, params=(username,))
            df['date'] = pd.to_datetime(df['date'])
            return df
    
    def update_transaction(self, transaction_id, date, type, category, amount, description):
        """Update an existing transaction"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE transactions 
                SET date = ?, type = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (date, type, category, amount, description, transaction_id))
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))

    def delete_all_user_transactions(self, username):
        """Delete all transactions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM transactions WHERE username = ?', (username,))
    
    def get_categories(self, type_filter=None):
        """Get all categories, optionally filtered by type"""
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT name FROM categories'
            params = ()
            if type_filter:
                query += ' WHERE type = ?'
                params = (type_filter,)
            query += ' ORDER BY name'
            
            result = conn.execute(query, params).fetchall()
            return [row[0] for row in result]
    
    def get_monthly_summary(self, username, year, month):
        """Get monthly summary data for a user"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT 
                    category,
                    type,
                    SUM(amount) as total
                FROM transactions
                WHERE username = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY category, type
            '''
            df = pd.read_sql_query(query, conn, params=(username, str(year), f'{month:02d}'))
            return df
    
    def get_cumulative_balance(self, username):
        """Get cumulative balance over time for a user"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT 
                    date,
                    SUM(CASE WHEN type = 'Income' THEN amount ELSE -amount END) as daily_change
                FROM transactions
                WHERE username = ?
                GROUP BY date
                ORDER BY date
            '''
            df = pd.read_sql_query(query, conn, params=(username,))
            df['date'] = pd.to_datetime(df['date'])
            df['cumulative_balance'] = df['daily_change'].cumsum()
            return df

    # Authentication methods
    def add_user(self, username, password, role='user'):
        """Add a new user"""
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, hashed, role)
                )
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, str(e)

    def verify_user(self, username, password):
        """Verify user credentials"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if result:
                stored_hash = result[0]
                role = result[1]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return True, role
            return False, None

    def update_password(self, username, new_password):
        """Update user password"""
        try:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (hashed, username)
                )
            return True, "Password updated successfully"
        except Exception as e:
            return False, str(e)

    def log_login(self, username, status):
        """Log login attempt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO login_logs (username, status) VALUES (?, ?)",
                (username, status)
            )

    def get_all_users(self):
        """Get all users"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT username, role, created_at FROM users", conn)

    def get_login_logs(self):
        """Get login logs"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM login_logs ORDER BY login_time DESC", conn)