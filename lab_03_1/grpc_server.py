import grpc
from concurrent import futures
import smart_home_pb2
import smart_home_pb2_grpc
import markdown

class SmartHomeService(smart_home_pb2_grpc.SmartHomeServiceServicer):
    
    # Метод 1: Умный дом
    def ControlDevice(self, request, context):
        command = request.command.lower()
        location = request.location
        
        print(f"\n[СЕРВЕР] Умный дом: {command} в {location}")
        
        if command == "включить свет":
            result = f"Свет на {location} включен"
            success = True
        elif command == "выключить свет":
            result = f"Свет на {location} выключен"
            success = True
        else:
            result = f"Неизвестная команда: {command}"
            success = False
        
        print(f"[СЕРВЕР] Ответ: {result}")
        return smart_home_pb2.DeviceResponse(result=result, success=success)
    
    # Метод 2: Конвертация Markdown в HTML
    def ConvertMarkdown(self, request, context):
        text = request.text
        
        print(f"\n[СЕРВЕР] Markdown конвертация ({len(text)} символов)")
        
        try:
            html = markdown.markdown(text)
            print(f"[СЕРВЕР] HTML сгенерирован")
            return smart_home_pb2.MarkdownResponse(html=html, success=True)
        except Exception as e:
            print(f"[СЕРВЕР] Ошибка: {e}")
            return smart_home_pb2.MarkdownResponse(html="", success=False)
    
    # Метод 3: Удаление дубликатов
    def RemoveDuplicates(self, request, context):
        words = list(request.words)
        
        print(f"\n[СЕРВЕР] Удаление дубликатов: {words}")
        
        try:
            seen = set()
            unique_words = []
            for word in words:
                if word not in seen:
                    seen.add(word)
                    unique_words.append(word)
            
            print(f"[СЕРВЕР] Уникальные: {unique_words}")
            return smart_home_pb2.DuplicateResponse(unique_words=unique_words, success=True)
        except Exception as e:
            print(f"[СЕРВЕР] Ошибка: {e}")
            return smart_home_pb2.DuplicateResponse(unique_words=[], success=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    smart_home_pb2_grpc.add_SmartHomeServiceServicer_to_server(
        SmartHomeService(), server
    )
    server.add_insecure_port('[::]:50051')
    print("=== gRPC сервер с 3 методами ===")
    print("1. ControlDevice - Умный дом")
    print("2. ConvertMarkdown - Markdown -> HTML")
    print("3. RemoveDuplicates - Удаление дубликатов")
    print("Сервер запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
