from flask import Flask, request, jsonify, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Подключение к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('ads.db')
    conn.row_factory = sqlite3.Row
    return conn

# Создание таблицы объявлений, если она не существует
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            owner TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Роут для создания объявления
@app.route('/ads', methods=['POST'])
def create_ad():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    owner = data.get('owner')

    if not title or not description or not owner:
        abort(400, description="Title, description, and owner are required fields.")

    created_at = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ads (title, description, created_at, owner)
        VALUES (?, ?, ?, ?)
    ''', (title, description, created_at, owner))
    conn.commit()
    ad_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': ad_id, 'message': 'Ad created successfully'}), 201

# Роут для получения объявления по ID
@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    conn = get_db_connection()
    ad = conn.execute('SELECT * FROM ads WHERE id = ?', (ad_id,)).fetchone()
    conn.close()

    if ad is None:
        abort(404, description="Ad not found")

    return jsonify({
        'id': ad['id'],
        'title': ad['title'],
        'description': ad['description'],
        'created_at': ad['created_at'],
        'owner': ad['owner']
    })

# Роут для удаления объявления по ID
@app.route('/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    conn = get_db_connection()
    result = conn.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
    conn.commit()
    conn.close()

    if result.rowcount == 0:
        abort(404, description="Ad not found")

    return jsonify({'message': 'Ad deleted successfully'}), 200

# Обработка ошибок
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': error.description}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': error.description}), 404

if __name__ == '__main__':
    app.run(debug=True)