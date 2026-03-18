from flask import Flask, request, jsonify, make_response
import json

app = Flask(__name__)

# Хранилище данных (в памяти)
schedule = []
next_id = 1

# Вспомогательная функция для поиска занятия
def find_lesson(lesson_id):
    return next((item for item in schedule if item["id"] == lesson_id), None)

# Функция для JSON с поддержкой кириллицы
def json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# КОРНЕВОЙ МАРШРУТ
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Расписания</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; margin: 40px; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>📚 API Расписания занятий</h1>
        <p>Сервер работает! Перейдите по ссылке:</p>
        <p><a href="/api/schedule">/api/schedule</a> - просмотр расписания</p>
    </body>
    </html>
    '''

# ПОЛУЧИТЬ ВСЁ РАСПИСАНИЕ (с кириллицей)
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    return json_response({"schedule": schedule})

# ДОБАВИТЬ НОВОЕ ЗАНЯТИЕ
@app.route('/api/schedule', methods=['POST'])
def add_lesson():
    global next_id
    data = request.get_json()
    
    if not data or not all(k in data for k in ("subject", "teacher", "time")):
        return json_response({"error": "Missing fields"}, 400)
    
    new_lesson = {
        "id": next_id,
        "subject": data["subject"],
        "teacher": data["teacher"],
        "time": data["time"]
    }
    schedule.append(new_lesson)
    next_id += 1
    return json_response(new_lesson, 201)

# ПОЛУЧИТЬ ОДНО ЗАНЯТИЕ ПО ID
@app.route('/api/schedule/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    lesson = find_lesson(lesson_id)
    if lesson:
        return json_response(lesson)
    return json_response({"error": "Lesson not found"}, 404)

# ОБНОВИТЬ ЗАНЯТИЕ
@app.route('/api/schedule/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    lesson = find_lesson(lesson_id)
    if not lesson:
        return json_response({"error": "Lesson not found"}, 404)
    
    data = request.get_json()
    lesson["subject"] = data.get("subject", lesson["subject"])
    lesson["teacher"] = data.get("teacher", lesson["teacher"])
    lesson["time"] = data.get("time", lesson["time"])
    return json_response(lesson)

# УДАЛИТЬ ЗАНЯТИЕ
@app.route('/api/schedule/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(lesson_id):
    global schedule
    lesson = find_lesson(lesson_id)
    if not lesson:
        return json_response({"error": "Lesson not found"}, 404)
    
    schedule = [item for item in schedule if item["id"] != lesson_id]
    return json_response({"message": "Lesson deleted"}, 200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
