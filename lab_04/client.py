import requests
import json
from cryptography.fernet import Fernet
import urllib3

# Отключаем предупреждения о самоподписанных сертификатах (только для лабораторной работы)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# ЗАГРУЗКА КЛЮЧА FERNET
# ============================================
with open('encryption_key.txt', 'rb') as f:
    fernet_key = f.read()
cipher = Fernet(fernet_key)

# ============================================
# ФУНКЦИЯ ОТПРАВКИ ЗАПРОСА
# ============================================
def send_analytics_request(numbers, operation):
    """Отправляет запрос координатору с числами и типом операции"""
    
    # 1. Формируем и шифруем полезную нагрузку
    payload = json.dumps({"numbers": numbers, "operation": operation})
    encrypted_payload = cipher.encrypt(payload.encode())
    
    # 2. Отправляем запрос координатору (c mTLS)
    coordinator_url = 'https://127.0.0.1:8000/api/analytics'
    cert = ('client_cert.pem', 'client_key.pem')
    
    try:
        resp = requests.post(
            coordinator_url,
            data=encrypted_payload,
            cert=cert,
            verify='ca_cert.pem',  # Проверка сертификата координатора/сервера
            timeout=10
        )
        
        # 3. Обрабатываем ответ
        if resp.status_code == 200:
            decrypted_response = cipher.decrypt(resp.content).decode()
            result = json.loads(decrypted_response)
            
            print(f"\n{'='*50}")
            print(f"РЕЗУЛЬТАТ:")
            
            if 'error' in result:
                print(f"  Ошибка: {result['error']}")
            else:
                op = result.get('operation', 'unknown')
                res = result.get('result')
                
                if op == 'sum':
                    print(f"  Сумма чисел: {res}")
                elif op == 'average':
                    print(f"  Среднее арифметическое: {res}")
                elif op == 'min_max':
                    print(f"  Минимальное значение: {res['min']}")
                    print(f"  Максимальное значение: {res['max']}")
                else:
                    print(f"  {op}: {res}")
            print(f"{'='*50}\n")
            
        else:
            print(f"\nОшибка HTTP: {resp.status_code}")
            try:
                error_data = resp.json()
                print(f"Детали: {error_data}")
            except:
                print(f"Тело ответа: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\nОшибка соединения: {e}")
        print("Убедитесь, что координатор запущен и серверы работают.")

# ============================================
# ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ
# ============================================
def print_menu():
    print("\n" + "="*50)
    print("КЛИЕНТ АНАЛИТИЧЕСКОЙ СИСТЕМЫ (Вариант 17)")
    print("="*50)
    print("\nДоступные операции:")
    print("  1 - Сумма чисел")
    print("  2 - Среднее арифметическое")
    print("  3 - Минимальное и максимальное значение")
    print("  0 - Выход")
    print("-"*50)

if __name__ == '__main__':
    while True:
        print_menu()
        
        # Выбор операции
        try:
            choice = input("Выберите операцию (0-3): ")
            if choice == '0':
                print("До свидания!")
                break
            
            if choice not in ['1', '2', '3']:
                print("Ошибка: выберите 1, 2, 3 или 0 для выхода.")
                continue
            
            # Ввод чисел
            numbers_input = input("Введите список чисел через пробел: ")
            numbers = [float(x) for x in numbers_input.split()]
            
            if len(numbers) == 0:
                print("Ошибка: введите хотя бы одно число.")
                continue
            
            # Определяем операцию
            if choice == '1':
                operation = 'sum'
            elif choice == '2':
                operation = 'avg'
            else:
                operation = 'min_max'
            
            # Отправляем запрос
            send_analytics_request(numbers, operation)
            
        except ValueError:
            print("Ошибка: введите корректные числа (например: 10 20 30)")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
