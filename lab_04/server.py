import ssl
import json
import sys
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet

# ============================================
# ЗАГРУЗКА КЛЮЧА FERNET
# ============================================
with open('encryption_key.txt', 'rb') as f:
    fernet_key = f.read()
cipher = Fernet(fernet_key)

# ============================================
# БИЗНЕС-ЛОГИКА (ВЫПОЛНЕНИЕ АНАЛИТИКИ)
# ============================================
def process_analytics(data_list, operation):
    """Выполняет аналитическую операцию над списком чисел."""
    if not data_list:
        return {"error": "Список чисел пуст."}
    
    if operation == 'sum':
        return {"result": sum(data_list), "operation": "sum"}
    elif operation == 'avg':
        return {"result": sum(data_list) / len(data_list), "operation": "average"}
    elif operation == 'min_max':
        return {"result": {"min": min(data_list), "max": max(data_list)}, "operation": "min_max"}
    else:
        return {"error": f"Неизвестная операция: {operation}"}

# ============================================
# FLASK ПРИЛОЖЕНИЕ
# ============================================
app = Flask(__name__)

@app.route('/api/analytics', methods=['POST'])
def analytics():
    try:
        # 1. Получение и расшифровка данных
        encrypted_data = request.get_data()
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        payload = json.loads(decrypted_data)
        
        numbers = payload.get('numbers')
        operation = payload.get('operation')
        
        # 2. Валидация
        if not isinstance(numbers, list) or not all(isinstance(i, (int, float)) for i in numbers):
            return jsonify({"error": "Некорректный формат данных. Требуется список чисел."}), 400
        
        # 3. Выполнение аналитики
        result = process_analytics(numbers, operation)
        
        # 4. Шифрование и отправка ответа
        response_json = json.dumps(result)
        encrypted_response = cipher.encrypt(response_json.encode())
        return encrypted_response, 200
        
    except Exception as e:
        print(f"Ошибка на сервере: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# ============================================
# ЗАПУСК СЕРВЕРА С mTLS
# ============================================
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')
    context.load_verify_locations('ca_cert.pem')
    context.verify_mode = ssl.CERT_REQUIRED
    
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=False)
