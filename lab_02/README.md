## 📅 Лабораторная работа №2

## Вариант 17

### Тема: Проектирование и реализация клиент-серверной системы. HTTP, веб-серверы и RESTful веб-сервисы

---

## Цель работы

Изучение принципов работы HTTP-протокола, получение навыков анализа REST API, разработки веб-сервисов на Flask и настройки обратного прокси-сервера Nginx с функцией кэширования.

---

## Задание

| № | Задание | Описание |
|---|---------|----------|
| 1 | HTTP-анализ | Анализ API randomuser.me для получения случайного пользователя |
| 2 | REST API "Бизнес-логика" | API для "Расписание занятий" (сущность: id, subject, teacher, time) |
| 3 | Настройка Nginx | Настройка Nginx как обратного прокси для Flask API |

---

## Архитектура решения

<img width="1280" height="665" alt="image" src="https://github.com/user-attachments/assets/f1f37e78-40b3-49ff-b79a-b0e749d06306" />

## Ход выполнения работы

### Задание 1. HTTP-анализ API randomuser.me

#### 1.1. Установка необходимых утилит

```
sudo apt update
sudo apt install curl -y
sudo apt install jq -y
```
<img width="1002" height="398" alt="image" src="https://github.com/user-attachments/assets/a6990fc1-e4db-4f3f-aff0-4803dd3371c2" />
<img width="1052" height="237" alt="image" src="https://github.com/user-attachments/assets/7e279de6-8d5f-4f91-866d-e8955830153a" />
<img width="1098" height="205" alt="image" src="https://github.com/user-attachments/assets/4aa80d0a-5e5f-4a35-8a7b-9c0bd09d8126" />

#### Проверка установки curl:

```
curl --version
```

<img width="1177" height="199" alt="image" src="https://github.com/user-attachments/assets/635ab60a-abcd-43dc-88a7-874d7a7df347" />

#### 1.2. Анализ структуры ответа
Простой запрос (нечитабельный ответ в виде одной непрерывной строки формата JSON):

```
curl https://randomuser.me/api/
```

<img width="1179" height="297" alt="image" src="https://github.com/user-attachments/assets/2467b4fe-4801-40d4-a724-086c81f57487" />

Форматированный вывод с помощью jq:

```
curl -s https://randomuser.me/api/ | jq
```

<img width="1215" height="793" alt="image" src="https://github.com/user-attachments/assets/532f4db2-f466-4a58-b0f4-d6d233b42926" />
<img width="1197" height="786" alt="image" src="https://github.com/user-attachments/assets/c990d7a4-026c-4431-99bd-7ae5f3b52fc9" />

Флаг -s (silent) убирает статистику загрузки.

Проанализируем структуру ответа:

* `results` — массив с одним пользователем;
* внутри: `gender, name, location, email, login, dob, registered, phone, cell, picture, nat`

#### 1.3. Команда 3. Анализ HTTP-заголовков

```
curl -i https://randomuser.me/api/
```

<img width="1203" height="671" alt="image" src="https://github.com/user-attachments/assets/99af4d8b-fc84-4349-b2f3-2abded77c12c" />

**Ключевые заголовки:**
* `HTTP/2 200` — код ответа
* `content-type:` application/json — формат данных
* `server:` — какой сервер
* `cache-control:` — политика кеширования

#### 1.4. Команда 4. Поиск заголовков (очень быстро), без тела ответа

```
curl -I https://randomuser.me/api/
```

<img width="1163" height="387" alt="image" src="https://github.com/user-attachments/assets/2944ea5a-63c9-46e8-852e-d12c637249d9" />

Далее - извлечение конкретных полей. Получим ФИ пользователя, его email и фото:

```
curl -s https://randomuser.me/api/ | jq '.results[0].name'
curl -s https://randomuser.me/api/ | jq '.results[0].email'
curl -s https://randomuser.me/api/ | jq '.results[0].picture.large'
```

<img width="1206" height="325" alt="image" src="https://github.com/user-attachments/assets/f50b895f-6ce5-454a-aa01-2e6f4f846e0c" />

### Задание 2. Разработка REST API "Расписание занятий"

#### 2.1. Структура данных "Занятие"

Каждый элемент расписания содержит следующие поля:

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | число | Уникальный идентификатор занятия (присваивается автоматически) |
| `subject` | строка | Название предмета |
| `teacher` | строка | ФИО преподавателя |
| `time` | строка | Время занятия в формате ISO (например, `2025-09-23T10:00:00`) |

Пример объекта:

```
{
  "id": 1,
  "subject": "Математика",
  "teacher": "Иванов И.И.",
  "time": "2025-09-23T10:00:00"
}
```

#### 2.2. Доступные операции (API Endpoints)

| Метод   | Эндпоинт              | Что делает                 |
|---------|-----------------------|----------------------------|
| GET     | `/api/schedule`       | Получить всё расписание    |
| POST    | `/api/schedule`       | Добавить новое занятие     |
| GET     | `/api/schedule/<id>`  | Получить одно занятие по ID |
| PUT     | `/api/schedule/<id>`  | Обновить занятие           |
| DELETE  | `/api/schedule/<id>`  | Удалить занятие            |

#### 2.2. Создание виртуального окружения и установка Flask:

```
cd ~/Downloads/Distributed_systems/practice/2026/lw_02/
mkdir schedule_api
cd schedule_api
python3 -m venv venv
source venv/bin/activate
pip install Flask
```

<img width="1205" height="620" alt="image" src="https://github.com/user-attachments/assets/d82803e1-1299-4a28-ae8b-50cd9fb9f5b7" />

#### 2.3. Реализация API (файл app.py)

Создадим файл `app.py` в папке `schedule_api` со следующим содержимым:

```
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
```

#### 2.4. Запуск Flask-приложения

```
python3 app.py
```

<img width="1167" height="278" alt="image" src="https://github.com/user-attachments/assets/4e8dd612-1be0-4a8f-83f9-85634b78ee4f" />

##### Добавление первого занятия (POST):

Команда `curl -X POST -H "Content-Type: application/json" \
  -d '{"subject": "Математика", "teacher": "Иванов И.И.", "time": "2025-09-23T10:00:00"}' \
  http://127.0.0.1:5000/api/schedule | jq`

<img width="1155" height="524" alt="image" src="https://github.com/user-attachments/assets/3bf336c0-cc90-4890-a79f-c77226ed75a0" />

Сервер отвечает на запрос и пишет дату создания занятия в левом терминале.
Для статистики и истории добавим второе занятие:

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"subject": "Физика", "teacher": "Петров П.П.", "time": "2025-09-23T12:00:00"}' \
  http://127.0.0.1:5000/api/schedule | jq
```

<img width="1149" height="518" alt="image" src="https://github.com/user-attachments/assets/c6e4090d-780d-4850-aa9a-fde96c22760b" />

С помощью команды `curl -s http://127.0.0.1:5000/api/schedule | jq` получим список полного расписания, которое у нас есть (GET):

<img width="572" height="436" alt="image" src="https://github.com/user-attachments/assets/fe31cf53-22e4-4b68-81c3-2695cd293fbc" />

С помощью команды `curl -s http://127.0.0.1:5000/api/schedule/1 | jq` получим занятие по ID (id: 1):

<img width="554" height="223" alt="image" src="https://github.com/user-attachments/assets/7da01a57-d13c-4982-a011-f2656f96c196" />

Обновим данные по занятию 1 (PUT): сменим ФИ и дату, а предмет оставим тем же:

```
curl -X PUT -H "Content-Type: application/json" \
  -d '{"teacher": "Сидоров С.С.", "time": "2025-09-23T11:00:00"}' \
  http://127.0.0.1:5000/api/schedule/1 | jq
```

<img width="576" height="433" alt="image" src="https://github.com/user-attachments/assets/9b417e83-5ebe-4a28-90c7-d1badc9160cc" />

Удалим занятие 1 (DELETED) и проверим, что оно удалилось, выведя содержание списка на экран терминала:

```
curl -X DELETE http://127.0.0.1:5000/api/schedule/1
```

<img width="563" height="432" alt="image" src="https://github.com/user-attachments/assets/360e3ecd-603f-4d3f-9dc4-ed7b46983aca" />

На каждый запрос сервер выдавал ответ с соответствующими HTTP-статусами (200, 201, 404).

<img width="594" height="519" alt="image" src="https://github.com/user-attachments/assets/afefeb93-3b2f-44ed-81f5-85e69df8b086" />

### Задание 3. Настройка Nginx как обратного прокси с кешированием
#### 3.1. Установка Nginx

`sudo apt update`
`sudo apt install nginx -y`

<img width="1139" height="717" alt="image" src="https://github.com/user-attachments/assets/fa02cd3f-58a6-4100-af3f-6595b3f2100d" />

`sudo systemctl start nginx`
`sudo systemctl enable nginx`

<img width="1107" height="145" alt="image" src="https://github.com/user-attachments/assets/c0d6719d-fcf0-43d2-bb50-f7e44ec26d81" />

Проверка статуса подключения Nginx:

`sudo systemctl status nginx`

<img width="1107" height="374" alt="image" src="https://github.com/user-attachments/assets/ccc9bb55-af3e-488d-9188-94f3ff436611" />

#### 3.2 Настройка кеширования (создание "склада")
Отредактируем главный конфиг Nginx:

```
sudo nano /etc/nginx/nginx.conf
```

Ответ терминала на команду:

<img width="1058" height="719" alt="image" src="https://github.com/user-attachments/assets/f7b36668-b9c7-4a7d-b43b-ef321681501c" />

В секции http { ... } (после настроек gzip) добавим строку:
```
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=schedule_cache:10m inactive=60m;
```

**Что означают параметры:**

* `/var/cache/nginx` — папка для хранения кеша
* `levels=1:2` — структура вложенности папок
* `keys_zone=schedule_cache:10m` — имя зоны кеша и размер в памяти
* `inactive=60m` — хранить неиспользуемый кеш 60 минут

Сохраняем файл: `Ctrl+X`, затем `Y`, затем `Enter`

#### 3.3. Настройка прокси для API
Отредактируем конфиг сайта по умолчанию:

```
sudo nano /etc/nginx/sites-available/default
```

<img width="1046" height="730" alt="image" src="https://github.com/user-attachments/assets/727efbb6-919d-46fd-8ce7-436b0d98c04c" />

В секции server { ... } после строки root /var/www/html; добавим:

```
location /api/ {
    # 1. Включаем кеширование
    proxy_cache schedule_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_valid 404 1m;
    add_header X-Cache-Status $upstream_cache_status;

    # 2. Прокси на Flask
    proxy_pass http://127.0.0.1:5000;

    # 3. Передаём оригинальные заголовки
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Сохраняем файл: `Ctrl+X`, затем `Y`, затем `Enter`

#### 3.4. Проверка конфигурации и перезапуск

```
sudo nginx -t
```

Сообщение об успешной настройке nginx: 

<img width="1009" height="98" alt="image" src="https://github.com/user-attachments/assets/6844b5a6-246d-4582-9ca8-1780e6d3bcab" />

### Подготовка к тестированию прокси

#### 📌 Тест 1. Проверка, работает ли Nginx сам по себе
Проверим, отвечает ли Nginx на обычные запросы (не к API) командой `curl http://localhost`:

<img width="1150" height="725" alt="image" src="https://github.com/user-attachments/assets/de07a709-d872-4444-8368-c9ddafa00c28" />

Это HTML-код приветственной страницы Nginx. Значит, Nginx работает!

#### 📌 Тест 2. Проверка проксирования (доступ к API через Nginx)
Теперь запросим API через Nginx (порт 80), а не напрямую к Flask (порт 5000):

`curl http://localhost/api/schedule`

<img width="1120" height="181" alt="image" src="https://github.com/user-attachments/assets/2fd748f9-9269-49bf-81af-aa40be6036c6" />

Cписок занятий пуст (так как были удалены все занятия). Tест пройден!

#### 📌 Тест 3. Проверка кеширования (HIT/MISS)
Это самый важный тест. Выполним команду `curl -i http://localhost/api/schedule | grep X-Cache-Status` два раза подряд:

<img width="744" height="516" alt="image" src="https://github.com/user-attachments/assets/032c4803-8691-4b82-b237-63dd8d472e8b" />

Значения:
* `EXPIRED`: кеш был, но истёк (прошло больше 5 минут). Nginx пошёл к Flask за свежими данными;
* `HIT`:  ответ взят из кеша.

Кэширование полностью настроено!

#### 📌 Тест 4. Проверка времени жизни кеша (5 минут)
Получили кэшированный ответ в тесте 3 (HIT), подождали 5 минут и снова выполнили запрос: видим expired и hit.
Все, как и должно быть!

<img width="1141" height="522" alt="image" src="https://github.com/user-attachments/assets/359ede62-323f-41ca-8770-2c910377c4e5" />

📌 Тест 5. Проверка, что POST не кэшируется
POST-запросы изменяют данные, поэтому они не должны кэшироваться.

Добавим новое занятие через Nginx:

```
curl -i -X POST -H "Content-Type: application/json" \
  -d '{"subject": "Информатика", "teacher": "Сидоров С.С.", "time": "2025-09-24T14:00:00"}' \
  http://localhost/api/schedule | grep X-Cache-Status
```

<img width="701" height="311" alt="image" src="https://github.com/user-attachments/assets/419f743d-ff95-464e-94dd-cf41f16e98b5" />

Важный момент: В выводе нет строки X-Cache-Status, потому что POST-запросы не кэшируются — это правильно!

#### 📌 Тест 6. Проверка, что новое занятие появилось в расписании

```
curl http://localhost/api/schedule | jq
```

<img width="1098" height="315" alt="image" src="https://github.com/user-attachments/assets/341aa04d-ec6d-493f-b139-89e964718483" />

## Архитектура инструментов REST API:

<img width="1280" height="538" alt="image" src="https://github.com/user-attachments/assets/238525da-f2c0-4587-bb45-e2ed854a74f7" />

## Архитектура инструментов REST API с Nginx:

<img width="1280" height="1235" alt="image" src="https://github.com/user-attachments/assets/278170c3-2155-408b-b38e-972ead176320" />

## Выводы:

В ходе выполнения лабораторной работы были успешно решены три задачи по теме "Проектирование и реализация клиент-серверной
системы. HTTP, веб-серверы и RESTful веб-сервисы".

На первом этапе проведён HTTP-анализ внешнего API "randomuser.me" с использованием утилиты curl. В результате анализа изучена структура JSON-ответа, отработаны навыки извлечения конкретных полей (ФИ, email, фото), а также исследованы HTTP-заголовки и параметры запроса для фильтрации данных.

На втором этапе разработано полноценное REST API на Python с использованием фреймворка Flask для управления расписанием занятий. Созданы четыре эндпоинта, реализующих CRUD-операции с сущностью «Занятие» (id, subject, teacher, time), данные хранятся в оперативной памяти. API успешно протестировано с помощью curl-запросов, подтверждена корректность обработки GET, POST, PUT и DELETE запросов.

На третьем этапе произведена настройка Nginx в качестве обратного прокси-сервера с функцией кэширования. В ходе настройки создана зона кэширования "schedule_cache", настроено проксирование запросов с порта 80 на Flask-приложение (порт 5000), добавлен заголовок "X-Cache-Status" для мониторинга состояния кэша. В процессе отладки были последовательно устранены ошибки конфигурации: исправлено имя зоны кэширования, удалены дублирующиеся директивы, скорректирован путь к папке кэша. 

Финальное тестирование подтвердило корректную работу проксирования и кэширования: при повторных запросах в течение пяти минут возвращается статус HIT, по истечении пяти минут — статус EXPIRED с последующим обновлением кэша. Таким образом, полученные мною навыки охватывают ключевые аспекты работы с HTTP-протоколом, разработки REST API и настройки обратного прокси-сервера с кэшированием.
