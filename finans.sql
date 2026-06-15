SELECT DATABASE();
CREATE DATABASE IF NOT EXISTS finance_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
USE finance_db;

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    amount DECIMAL(10, 2) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Начальный баланс 10000
INSERT INTO transactions (amount, type, category, description, date) VALUES
(10000.00, 'income', 'Начальный баланс', 'Начальный баланс счета', CURDATE());

-- Тестовые транзакции
INSERT INTO transactions (amount, type, category, description, date) VALUES
(50000.00, 'income', 'Зарплата', 'Зарплата за январь 2026', '2026-01-15'),
(3500.00, 'expense', 'Продукты', 'Покупка продуктов в супермаркете', '2026-01-16'),
(1200.00, 'expense', 'Транспорт', 'Проездной на месяц', '2026-01-17'),
(2500.00, 'expense', 'Ресторан', 'Ужин с друзьями', '2026-01-18'),
(15000.00, 'income', 'Фриланс', 'Оплата за проект', '2026-01-20'),
(800.00, 'expense', 'Развлечения', 'Кино и попкорн', '2026-01-22'),
(3000.00, 'expense', 'Одежда', 'Покупка зимней куртки', '2026-01-25'),
(2000.00, 'expense', 'Коммунальные услуги', 'Оплата за электричество', '2026-01-28'),
(2500.00, 'expense', 'Здоровье', 'Витамины и лекарства', '2026-01-30'),
(45000.00, 'income', 'Зарплата', 'Зарплата за февраль 2026', '2026-02-15');

SELECT 
    id,
    DATE_FORMAT(date, '%d.%m.%Y') AS дата,
    CASE 
        WHEN type = 'income' THEN 'Доход'
        ELSE 'Расход'
    END AS тип,
    category AS категория,
    description AS описание,
    CONCAT(FORMAT(amount, 2), ' ₽') AS сумма
FROM transactions
ORDER BY date DESC, id DESC;

SELECT 
    'Общая статистика' AS показатели,
    CONCAT(FORMAT(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 2), ' ₽') AS доходы,
    CONCAT(FORMAT(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 2), ' ₽') AS расходы,
    CONCAT(FORMAT(SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 2), ' ₽') AS баланс
FROM transactions;

SELECT 
    category AS категория,
    COUNT(*) AS количество,
    CONCAT(FORMAT(SUM(amount), 2), ' ₽') AS сумма,
    CONCAT(FORMAT(AVG(amount), 2), ' ₽') AS средний_чек
FROM transactions
WHERE type = 'expense'
GROUP BY category
ORDER BY SUM(amount) DESC;

SELECT 
    category AS категория,
    COUNT(*) AS количество,
    CONCAT(FORMAT(SUM(amount), 2), ' ₽') AS сумма
FROM transactions
WHERE type = 'income'
GROUP BY category
ORDER BY SUM(amount) DESC;

SELECT 
    'Проверка данных:' AS '',
    COUNT(*) AS всего_транзакций,
    MIN(date) AS самая_ранняя_дата,
    MAX(date) AS самая_поздняя_дата,
    ROUND(AVG(amount), 2) AS средняя_сумма
FROM transactions;