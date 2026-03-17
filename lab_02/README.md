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



