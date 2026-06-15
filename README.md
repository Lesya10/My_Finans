# Личные финансы - приложение для управления бюджетом

Веб-приложение для учета доходов и расходов с хранением данных в MySQL.

## Функциональность

- Добавление доходов и расходов
- Категоризация транзакций
- Просмотр истории операций
- Статистика (общие доходы, расходы, баланс)
- Удаление транзакций

## Технологии

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Frontend**: HTML, CSS (встроенные)

## Установка и запуск

### Требования

- Python 3.8+
- MySQL 5.7+

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Lesya10/My_Finans
cd finance-app

### Шаг 2: установка зависимостей
pip install fastapi uvicorn sqlalchemy pymysql

### Шаг 3: запуск Mysql
## Создание бд
mysql -u root -p
##Введите пароль, затем создайте таблицы
sql
CREATE DATABASE finance_db;
USE finance_db;

CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    amount DECIMAL(10,2) NOT NULL,
    type VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    date VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

EXIT;

### Шаг 4: запуск приложения
python app.py

### Шаг 5: перейдите по ссылке
http://127.0.0.1:8000