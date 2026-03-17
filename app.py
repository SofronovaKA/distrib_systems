from flask import Flask, request, jsonify

app = Flask(__name__)

# Хранилище данных (в памяти)
schedule = []
next_id = 1

# Вспомогательная функция для поиска занятия
def find_lesson(lesson_id):
    return next((item for item in schedule if item["id"] == lesson_id), None)

# 1. ПОЛУЧИТЬ ВСЁ РАСПИСАНИЕ
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    return jsonify({"schedule": schedule})

# 2. ДОБАВИТЬ НОВОЕ ЗАНЯТИЕ
@app.route('/api/schedule', methods=['POST'])
def add_lesson():
    global next_id
    data = request.get_json()
    
    # Валидация
    if not data or not all(k in data for k in ("subject", "teacher", "time")):
        return jsonify({"error": "Missing fields"}), 400
    
    new_lesson = {
        "id": next_id,
        "subject": data["subject"],
        "teacher": data["teacher"],
        "time": data["time"]
    }
    schedule.append(new_lesson)
    next_id += 1
    return jsonify(new_lesson), 201

# 3. ПОЛУЧИТЬ ОДНО ЗАНЯТИЕ ПО ID
@app.route('/api/schedule/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    lesson = find_lesson(lesson_id)
    if lesson:
        return jsonify(lesson)
    return jsonify({"error": "Lesson not found"}), 404

# 4. ОБНОВИТЬ ЗАНЯТИЕ
@app.route('/api/schedule/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    lesson = find_lesson(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    
    data = request.get_json()
    lesson["subject"] = data.get("subject", lesson["subject"])
    lesson["teacher"] = data.get("teacher", lesson["teacher"])
    lesson["time"] = data.get("time", lesson["time"])
    return jsonify(lesson)

# 5. УДАЛИТЬ ЗАНЯТИЕ
@app.route('/api/schedule/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(lesson_id):
    global schedule
    lesson = find_lesson(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    
    schedule = [item for item in schedule if item["id"] != lesson_id]
    return jsonify({"message": "Lesson deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
