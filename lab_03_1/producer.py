import pika
import json
import sys

credentials = pika.PlainCredentials('user', 'password')

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
)
channel = connection.channel()

channel.queue_declare(queue='tasks_queue', durable=True)

def show_menu():
    print("\n" + "="*50)
    print("Выберите тип задания:")
    print("="*50)
    print("1. 🏠 Умный дом (включить/выключить свет)")
    print("2. 📝 Конвертер Markdown -> HTML")
    print("3. 🔄 Удаление дубликатов из списка")
    print("0. ❌ Выход")
    print("="*50)

def send_smart_home(channel):
    print("\n--- Умный дом ---")
    print("Команды: включить свет, выключить свет")
    command = input("Введите команду: ").strip().lower()
    
    if command not in ["включить свет", "выключить свет"]:
        print("❌ Неверная команда! Используйте 'включить свет' или 'выключить свет'")
        return
    
    location = input("Введите место (кухня, гостиная и т.д.): ").strip()
    if not location:
        location = "кухня"
    
    task = {
        "type": "smart_home",
        "data": {
            "command": command,
            "location": location
        }
    }
    
    send_message(channel, task)
    print(f"✅ Отправлено: {command} в {location}")

def send_markdown(channel):
    print("\n--- Конвертер Markdown -> HTML ---")
    print("Пример Markdown:")
    print("  # Заголовок")
    print("  **жирный текст**")
    print("  *курсив*")
    print("  - список")
    print("(Для завершения ввода введите пустую строку и нажмите Enter)")
    
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    text = "\n".join(lines)
    
    if not text:
        print("❌ Текст не введен!")
        return
    
    task = {
        "type": "markdown",
        "data": {"text": text}
    }
    
    send_message(channel, task)
    print(f"✅ Отправлен Markdown текст ({len(text)} символов)")

def send_deduplicate(channel):
    print("\n--- Удаление дубликатов ---")
    print("Введите слова/элементы через пробел:")
    print("Пример: яблоко банан яблоко апельсин банан груша")
    
    user_input = input("> ").strip()
    
    if not user_input:
        print("❌ Список не введен!")
        return
    
    words = user_input.split()
    
    task = {
        "type": "deduplicate",
        "data": {"words": words}
    }
    
    send_message(channel, task)
    print(f"✅ Отправлен список: {words}")

def send_message(channel, task):
    message = json.dumps(task, ensure_ascii=False)
    channel.basic_publish(
        exchange='',
        routing_key='tasks_queue',
        body=message.encode('utf-8'),
        properties=pika.BasicProperties(delivery_mode=2)
    )

def main():
    print("\n" + "="*50)
    print("   ИНТЕРАКТИВНЫЙ PRODUCER ДЛЯ RABBITMQ")
    print("="*50)
    print("Отправляйте задания в очередь 'tasks_queue'")
    print("Веб-интерфейс RabbitMQ: http://localhost:15672")
    print("Логин: user, Пароль: password")
    
    while True:
        show_menu()
        choice = input("Ваш выбор: ").strip()
        
        if choice == '1':
            send_smart_home(channel)
        elif choice == '2':
            send_markdown(channel)
        elif choice == '3':
            send_deduplicate(channel)
        elif choice == '0':
            print("\nВыход из программы. До свидания!")
            break
        else:
            print("❌ Неверный выбор! Попробуйте снова.")
    
    connection.close()

if __name__ == '__main__':
    main()
