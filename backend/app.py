from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

# ---------------- Database Setup ----------------
# Use SQLite for mock inventory (run this only once to create table and add data)
def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 category TEXT,
                 price REAL,
                 description TEXT)
              ''')

    # Insert mock data (only once)
    for i in range(1, 101):
        c.execute("INSERT INTO products (name, category, price, description) VALUES (?, ?, ?, ?)",
                  (f"Product {i}", "Books", round(random.uniform(10, 100), 2), f"Description of product {i}"))
    conn.commit()
    conn.close()

# init_db()  # Uncomment this to create and populate the DB

# ---------------- Routes ----------------
@app.route('/api/search', methods=['POST'])
def search_products():
    query = request.json.get('query', '').lower()
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?", (f"%{query}%", f"%{query}%"))
    results = c.fetchall()
    conn.close()

    # Save session history
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session.setdefault('history', []).append({'query': query, 'timestamp': timestamp})

    return jsonify([{'id': row[0], 'name': row[1], 'category': row[2], 'price': row[3], 'description': row[4]} for row in results])

@app.route('/api/history')
def get_history():
    return jsonify(session.get('history', []))

# ---------------- Run Server ----------------
if __name__ == '__main__':
    app.run(debug=True)
