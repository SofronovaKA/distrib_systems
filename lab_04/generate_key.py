from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open('encryption_key.txt', 'wb') as f:
    f.write(key)
print("Ключ сохранён в encryption_key.txt")
