import sqlite3
import pandas as pd
import datetime

DB_NAME = "bookkeeper.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Invoices Table (Money In)
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            invoice_no TEXT,
            customer_name TEXT,
            gstin TEXT,
            taxable_value REAL,
            gst_rate REAL,
            igst REAL,
            cgst REAL,
            sgst REAL,
            total_amount REAL,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')

    # Expenses Table (Money Out)
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            vendor_name TEXT,
            gstin TEXT,
            category TEXT,
            taxable_value REAL,
            gst_rate REAL,
            igst REAL,
            cgst REAL,
            sgst REAL,
            total_amount REAL,
            description TEXT
        )
    ''')

    # Notifications & Tasks Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT, -- 'Notice', 'Challan', 'Reminder'
            description TEXT,
            action_required TEXT,
            status TEXT DEFAULT 'Pending' -- 'Pending', 'Acknowledged', 'Paid'
        )
    ''')
    
    conn.commit()
    conn.close()

def add_invoice(date, invoice_no, customer_name, gstin, taxable_value, gst_rate, igst, cgst, sgst, total_amount):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO invoices (date, invoice_no, customer_name, gstin, taxable_value, gst_rate, igst, cgst, sgst, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, invoice_no, customer_name, gstin, taxable_value, gst_rate, igst, cgst, sgst, total_amount))
    conn.commit()
    conn.close()

def get_invoices():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM invoices ORDER BY date DESC", conn)
    conn.close()
    return df

def add_expense(date, vendor_name, gstin, category, taxable_value, gst_rate, igst, cgst, sgst, total_amount, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (date, vendor_name, gstin, category, taxable_value, gst_rate, igst, cgst, sgst, total_amount, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, vendor_name, gstin, category, taxable_value, gst_rate, igst, cgst, sgst, total_amount, description))
    conn.commit()
    conn.close()

def get_expenses():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    return df

def add_notification(date, type, description, action_required):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO notifications (date, type, description, action_required, status)
        VALUES (?, ?, ?, ?, 'Pending')
    ''', (date, type, description, action_required))
    conn.commit()
    conn.close()

def get_notifications(pending_only=False):
    conn = get_connection()
    query = "SELECT * FROM notifications ORDER BY date DESC"
    if pending_only:
        query = "SELECT * FROM notifications WHERE status='Pending' ORDER BY date DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_notification_status(id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE notifications SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()

# Initialize DB on import (will create new table if missing)
init_db()
