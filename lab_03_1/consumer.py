import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'grpc_sync'))

import pika
import grpc
import smart_home_pb2
import smart_home_pb2_grpc

credentials = pika.PlainCredentials('user', 'password')

def process_smart_home(data, stub):
    """Вызывает метод ControlDevice"""
    command = data.get('command', '')
    location = data.get('location', 'кухня')
    
    response = stub.ControlDevice(
        smart_home_pb2.DeviceRequest(
            command=command.strip(),
            location=location.strip()
        )
    )
    return response.result, response.success

def process_markdown(data, stub):
    """Вызывает метод ConvertMarkdown"""
    text = data.get('text', '')
    
    response = stub.ConvertMarkdown(
        smart_home_pb2.MarkdownRequest(text=text)
    )
    return response.html, response.success

def process_deduplicate(data, stub):
    """Вызывает метод RemoveDuplicates"""
    words = data.get('words', [])
    
    response = stub.RemoveDuplicates(
        smart_home_pb2.DuplicateRequest(words=words)
    )
    return response.unique_words, response.success

def callback(ch, method, properties, body):
    try:
        message = json.loads(body.decode('utf-8'))
        task_type = message.get('type')
        data = message.get('data', {})
        
        print(f"\n📨 Получено: {task_type}")
        
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = smart_home_pb2_grpc.SmartHomeServiceStub(channel)
            
            if task_type == 'smart_home':
                result, success = process_smart_home(data, stub)
                print(f"🏠 Результат: {result}")
                
            elif task_type == 'markdown':
                result, success = process_markdown(data, stub)
                print(f"📝 HTML (первые 100 символов): {result[:100]}...")
                
            elif task_type == 'deduplicate':
                result, success = process_deduplicate(data, stub)
                print(f"🔄 Уникальные: {result}")
                
            else:
                print(f"❌ Неизвестный тип: {task_type}")
                success = False
            
            print(f"✅ Статус: {'УСПЕШНО' if success else 'ОШИБКА'}")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=credentials
            )
        )
        channel = connection.channel()
        
        channel.queue_declare(queue='tasks_queue', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='tasks_queue', on_message_callback=callback)
        
        print("✅ Consumer готов! Ожидание заданий...")
        channel.start_consuming()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
