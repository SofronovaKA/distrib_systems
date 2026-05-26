# 1. Генерация Центра Сертификации (CA)
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
  -keyout ca_key.pem -out ca_cert.pem \
  -subj "/CN=MyCA"

# 2. Генерация ключа и запроса на сертификат (CSR) для Сервера
openssl req -newkey rsa:4096 -nodes -keyout server_key.pem -out server.csr \
  -subj "/CN=server"

# 3. Подпись сертификата сервера
openssl x509 -req -in server.csr -days 365 -CA ca_cert.pem -CAkey ca_key.pem \
  -CAcreateserial -out server_cert.pem

# 4. Генерация ключа и запроса для Клиента
openssl req -newkey rsa:4096 -nodes -keyout client_key.pem -out client.csr \
  -subj "/CN=client"

# 5. Подпись сертификата клиента
openssl x509 -req -in client.csr -days 365 -CA ca_cert.pem -CAkey ca_key.pem \
  -CAcreateserial -out client_cert.pem

# 6. Очистка
rm client.csr server.csr
echo "Готово!"
