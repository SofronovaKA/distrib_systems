import grpc
import calendar_pb2
import calendar_pb2_grpc

def run():
    # Подключаемся к серверу
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = calendar_pb2_grpc.CalendarServiceStub(channel)
        
        while True:
            print("\n--- МЕНЮ ---")
            print("1. Создать новое событие")
            print("2. Посмотреть список всех событий")
            print("3. Выход")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                print("\n--- Создание нового события ---")
                title = input("Название: ")
                description = input("Описание: ")
                start = input("Время начала: ")
                end = input("Время окончания: ")
                
                # Собираем сообщение для отправки
                request = calendar_pb2.EventDetails(
                    title=title,
                    description=description,
                    start_time=start,
                    edd_time=end,
                    participants=["Я"]
                )
                
                # Отправляем на сервер
                response = stub.CreateEvent(request)
                print(f"Успешно! ID события: {response.event_id}")
                
            elif choice == "2":
                print("\n--- Запрос списка событий ---")
                try:
                    # Вызываем новый метод. Передаем пустой объект Empty()
                    # так как ListEvents по протоколу требует Empty на вход
                    response = stub.ListEvents(calendar_pb2.Empty())
                    
                    print(f"Найдено событий в базе: {response.total_count}")
                    
                    if response.total_count == 0:
                        print("Каталог пока пуст.")
                    else:
                        for i, event in enumerate(response.events, 1):
                            print(f"{i}. {event.title} [{event.start_time} - {event.edd_time}]")
                            print(f"   Описание: {event.description}")
                
                except grpc.RpcError as e:
                    print(f"Ошибка gRPC: {e.code()} - {e.details()}")
            
            elif choice == "3":
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор, попробуйте снова.")

if __name__ == '__main__':
    run()