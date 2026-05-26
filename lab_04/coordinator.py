import requests
from flask import Flask, request, Response
import urllib3
import ssl

# Отключаем предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# КАСТОМНЫЙ АДАПТЕР ДЛЯ ОТКЛЮЧЕНИЯ ПРОВЕРКИ HOSTNAME
# ============================================
class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['assert_hostname'] = False
        return super().init_poolmanager(*args, **kwargs)

# Создаём сессию с кастомным адаптером
session = requests.Session()
session.mount('https://', CustomHTTPAdapter())

# ============================================
# НАСТРОЙКА ПРИЛОЖЕНИЯ
# ============================================
app = Flask(__name__)

# Список серверов в порядке приоритета
SERVERS = [
    'https://127.0.0.1:5001/api/analytics',
    'https://127.0.0.1:5002/api/analytics'
]

# Пути к сертификатам для mTLS
CERT = ('client_cert.pem', 'client_key.pem')
CA_CERT = 'ca_cert.pem'  # всё равно не используется из-за verify=False

# ============================================
# ОСНОВНОЙ МАРШРУТ
# ============================================
@app.route('/api/analytics', methods=['POST'])
def proxy_analytics():
    """Принимает запрос от клиента и перенаправляет на доступный сервер"""
    client_data = request.get_data()
    
    for server_url in SERVERS:
        try:
            # Используем нашу сессию с отключенной проверкой hostname
            resp = session.post(
                server_url,
                data=client_data,
                cert=CERT,
                verify=False,  # Отключаем проверку сертификата (только для лабы)
                timeout=5
            )
            # Если успешно — возвращаем ответ клиенту
            return Response(
                resp.content, 
                status=resp.status_code, 
                content_type=resp.headers.get('content-type', 'application/octet-stream')
            )
        
        except requests.exceptions.SSLError as e:
            print(f"SSL ошибка при подключении к {server_url}: {e}")
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения к {server_url}: {e}")
            continue
        except Exception as e:
            print(f"Неизвестная ошибка при подключении к {server_url}: {e}")
            continue
    
    # Если все серверы недоступны
    return {"error": "Все серверы недоступны"}, 503

# ============================================
# ЗАПУСК
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("КООРДИНАТОР ЗАПУЩЕН")
    print("=" * 50)
    print(f"Порт: 8000 (HTTP)")
    print(f"Серверы в списке: {SERVERS}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8000, debug=False)
