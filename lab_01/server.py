import grpc
from concurrent import futures
import uuid
import time

# Импортируем сгенерированные файлы 
import calendar_pb2
import calendar_pb2_grpc

class CalendarService(calendar_pb2_grpc.CalendarServiceServicer):
    
    def __init__(self):
        # Это список, который будет хранить все твои события в памяти сервера.
        self.events_db = []
        print("Сервис календаря инициализирован. База пуста.")

    def CreateEvent(self, request, context):
        """Метод вызывается при нажатии '1' в клиенте"""
        print(f"--- Получен запрос на создание: {request.title} ---")
        
        # Сохраняем событие целиком в наш список
        self.events_db.append(request)
        
        # Генерируем ID для ответа
        generated_id = str(uuid.uuid4())
        print(f"Событие сохранено. Всего в базе: {len(self.events_db)}")
        
        return calendar_pb2.CreateEventResponse(
            event_id=generated_id,
            success=True
        )

    def ListEvents(self, request, context):
        """Метод вызывается при нажатии '2' в клиенте"""
        print(f"--- Запрос списка событий (всего: {len(self.events_db)}) ---")
        
        # Возвращаем объект EventList, который мы прописали в .proto
        return calendar_pb2.EventList(
            events=self.events_db,
            total_count=len(self.events_db)
        )

def serve():
    # Создаем сервер
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Регистрируем наш класс CalendarService на сервере
    calendar_pb2_grpc.add_CalendarServiceServicer_to_server(CalendarService(), server)
    
    # Слушаем порт 50051
    server.add_insecure_port('[::]:50051')
    print("СЕРВЕР ЗАПУЩЕН на порту 50051...")
    print("Нажми Ctrl+C для остановки")
    
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()