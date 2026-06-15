from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pymysql
import re

MYSQL_PASSWORD = "olesya10"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_DATABASE = "finance_db"


DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель транзакции
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    type = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    date = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_transaction_data(amount, category, date, description=None):
    """Валидация данных транзакции - исправление всех ошибок"""
    
    # Ошибка 1 и 2: Проверка суммы (не отрицательная и не нулевая)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть больше 0")
    
    # Ошибка 5: Проверка максимальной суммы
    if amount > 10000000:
        raise HTTPException(status_code=400, detail="Сумма не может превышать 10,000,000 ₽")
    
    # Ошибка 3: Проверка категории (не пустая)
    if not category or not category.strip():
        raise HTTPException(status_code=400, detail="Категория не может быть пустой")
    
    # Ошибка 4: Проверка длины категории
    if len(category) > 50:
        raise HTTPException(status_code=400, detail="Категория не может быть длиннее 50 символов")
    
    # Дополнительная проверка: недопустимые символы в категории
    if not re.match(r'^[а-яА-Яa-zA-Z0-9\s\-]+$', category):
        raise HTTPException(status_code=400, detail="Категория содержит недопустимые символы")
    
    # Ошибка 6: Проверка длины описания
    if description and len(description) > 200:
        raise HTTPException(status_code=400, detail="Описание не может быть длиннее 200 символов")
    
    # Проверка формата даты
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD")
    
    # Проверка типа транзакции
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Тип транзакции должен быть 'income' или 'expense'")
    
    return True
# ==================== КОНЕЦ ДОБАВЛЕННОЙ ФУНКЦИИ ====================

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Личные финансы</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #f0f2f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            padding: 40px 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }

        /* Header */
        .header {
            background: #1a1a2e;
            color: white;
            padding: 32px 40px;
            border-bottom: 1px solid #16213e;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }

        .header p {
            color: #a0a0a0;
            font-size: 14px;
        }

        /* Content */
        .content {
            padding: 40px;
        }

        /* Form */
        .form-section {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 40px;
            border: 1px solid #e9ecef;
        }

        .form-title {
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e9ecef;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-size: 13px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input,
        .form-group select {
            padding: 12px 16px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.2s ease;
            background: white;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #1a1a2e;
            box-shadow: 0 0 0 3px rgba(26, 26, 46, 0.1);
        }

        .btn-primary {
            background: #1a1a2e;
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            width: auto;
            min-width: 200px;
        }

        .btn-primary:hover {
            background: #16213e;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(26, 26, 46, 0.2);
        }

        /* Stats Cards */
        .stats-section {
            margin-bottom: 40px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }

        .stat-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.2s ease;
        }

        .stat-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        .stat-card .stat-label {
            font-size: 13px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .stat-card .stat-value {
            font-size: 36px;
            font-weight: 700;
            color: #1a1a2e;
        }

        .stat-card.income .stat-value {
            color: #2ecc71;
        }

        .stat-card.expense .stat-value {
            color: #e74c3c;
        }

        .stat-card.balance .stat-value {
            color: #1a1a2e;
        }

        /* Transactions Table */
        .transactions-section {
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            overflow: hidden;
        }

        .transactions-header {
            padding: 24px 32px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .transactions-header h2 {
            font-size: 18px;
            font-weight: 600;
            color: #1a1a2e;
        }

        .transactions-count {
            font-size: 13px;
            color: #6c757d;
            background: #e9ecef;
            padding: 4px 10px;
            border-radius: 20px;
        }

        .transactions-table {
            width: 100%;
            border-collapse: collapse;
        }

        .transactions-table th {
            text-align: left;
            padding: 16px 20px;
            background: #f8f9fa;
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #e9ecef;
        }

        .transactions-table td {
            padding: 16px 20px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
        }

        .transactions-table tr:hover {
            background: #f8f9fa;
        }

        .transaction-category {
            font-weight: 600;
            color: #1a1a2e;
        }

        .transaction-date {
            color: #6c757d;
            font-size: 12px;
        }

        .transaction-description {
            color: #868e96;
            font-size: 13px;
            margin-top: 4px;
        }

        .transaction-amount {
            font-weight: 600;
            font-size: 15px;
        }

        .transaction-amount.income {
            color: #2ecc71;
        }

        .transaction-amount.expense {
            color: #e74c3c;
        }

        .delete-btn {
            background: none;
            border: none;
            color: #e74c3c;
            cursor: pointer;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            transition: all 0.2s ease;
            width: auto;
        }

        .delete-btn:hover {
            background: #fee;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .content {
                padding: 20px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .transactions-table th,
            .transactions-table td {
                padding: 12px;
            }
            
            .transactions-table {
                font-size: 12px;
            }
            
            .btn-primary {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Личные финансы</h1>
            <p>Управление доходами и расходами</p>
        </div>

        <div class="content">
            <!-- Форма добавления -->
            <div class="form-section">
                <div class="form-title">Новая транзакция</div>
                <form id="form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Сумма</label>
                            <input type="number" id="amount" placeholder="0.00" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Тип</label>
                            <select id="type">
                                <option value="expense">Расход</option>
                                <option value="income">Доход</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Категория</label>
                            <select id="category">
                                <option value="Продукты">Продукты</option>
                                <option value="Транспорт">Транспорт</option>
                                <option value="Развлечения">Развлечения</option>
                                <option value="Одежда">Одежда</option>
                                <option value="Зарплата">Зарплата</option>
                                <option value="Фриланс">Фриланс</option>
                                <option value="Ресторан">Ресторан</option>
                                <option value="Здоровье">Здоровье</option>
                                <option value="Коммунальные услуги">Коммунальные услуги</option>
                                <option value="Другое">Другое</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Описание</label>
                            <input type="text" id="description" placeholder="Описание транзакции">
                        </div>
                        <div class="form-group">
                            <label>Дата</label>
                            <input type="date" id="date">
                        </div>
                    </div>
                    <button type="submit" class="btn-primary">Добавить транзакцию</button>
                </form>
            </div>

            <!-- Статистика -->
            <div class="stats-section">
                <div class="stats-grid">
                    <div class="stat-card income">
                        <div class="stat-label">Доходы</div>
                        <div class="stat-value" id="income">0 ₽</div>
                    </div>
                    <div class="stat-card expense">
                        <div class="stat-label">Расходы</div>
                        <div class="stat-value" id="expense">0 ₽</div>
                    </div>
                    <div class="stat-card balance">
                        <div class="stat-label">Баланс</div>
                        <div class="stat-value" id="balance">0 ₽</div>
                    </div>
                </div>
            </div>

            <!-- Список транзакций -->
            <div class="transactions-section">
                <div class="transactions-header">
                    <h2>История операций</h2>
                    <div class="transactions-count" id="transactions-count">0 записей</div>
                </div>
                <div id="transactions"></div>
            </div>
        </div>
    </div>

    <script>
        async function load() {
            try {
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                document.getElementById('income').innerHTML = stats.income.toFixed(2) + ' ₽';
                document.getElementById('expense').innerHTML = stats.expense.toFixed(2) + ' ₽';
                document.getElementById('balance').innerHTML = stats.balance.toFixed(2) + ' ₽';
                
                const transRes = await fetch('/api/transactions');
                const transactions = await transRes.json();
                
                document.getElementById('transactions-count').innerHTML = transactions.length + ' записей';
                
                const container = document.getElementById('transactions');
                if (!transactions.length) {
                    container.innerHTML = '<div class="empty-state">Нет транзакций. Добавьте первую запись</div>';
                    return;
                }
                
                let tableHtml = `
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Категория</th>
                                <th>Описание</th>
                                <th>Дата</th>
                                <th>Сумма</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                transactions.forEach(t => {
                    const amountClass = t.type === 'income' ? 'income' : 'expense';
                    const sign = t.type === 'income' ? '+' : '-';
                    tableHtml += `
                        <tr>
                            <td>
                                <div class="transaction-category">${t.category}</div>
                            </td>
                            <td>
                                <div>${t.description || '—'}</div>
                            </td>
                            <td>
                                <div class="transaction-date">${t.date}</div>
                            </td>
                            <td>
                                <div class="transaction-amount ${amountClass}">${sign} ${t.amount.toFixed(2)} ₽</div>
                            </td>
                            <td>
                                <button class="delete-btn" onclick="del(${t.id})">Удалить</button>
                            </td>
                        </tr>
                    `;
                });
                
                tableHtml += `
                        </tbody>
                    </table>
                `;
                
                container.innerHTML = tableHtml;
            } catch(e) {
                console.error(e);
                document.getElementById('transactions').innerHTML = '<div class="empty-state">Ошибка загрузки данных</div>';
            }
        }
        
        async function del(id) {
            if (confirm('Удалить эту транзакцию?')) {
                await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
                load();
            }
        }
        
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            const amount = parseFloat(document.getElementById('amount').value);
            if (!amount || amount <= 0) {
                alert('Введите корректную сумму');
                return;
            }
            
            const data = new URLSearchParams();
            data.append('amount', amount);
            data.append('type', document.getElementById('type').value);
            data.append('category', document.getElementById('category').value);
            data.append('description', document.getElementById('description').value);
            data.append('date', document.getElementById('date').value || new Date().toISOString().split('T')[0]);
            
            const res = await fetch('/api/transactions', { method: 'POST', body: data });
            if (res.ok) {
                document.getElementById('form').reset();
                load();
            } else {
                alert('Ошибка при добавлении');
            }
        };
        
        load();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=HTML)

@app.post("/api/transactions")
async def create_transaction(
    amount: float = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    date: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        validate_transaction_data(amount, category, date, description)
        
        transaction = Transaction(
            amount=amount,
            type=type,
            category=category,
            description=description,
            date=date
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return {"ok": True, "id": transaction.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/transactions")
async def get_transactions(db: Session = Depends(get_db)):
    try:
        transactions = db.query(Transaction).order_by(Transaction.date.desc()).all()
        return [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "category": t.category,
                "description": t.description,
                "date": t.date
            }
            for t in transactions
        ]
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/transactions/{id}")
async def delete_transaction(id: int, db: Session = Depends(get_db)):
    try:
        transaction = db.query(Transaction).filter(Transaction.id == id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        db.delete(transaction)
        db.commit()
        return {"ok": True}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    try:
        transactions = db.query(Transaction).all()
        income = sum(t.amount for t in transactions if t.type == "income")
        expense = sum(t.amount for t in transactions if t.type == "expense")
        return {
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": round(income - expense, 2)
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("="*50)
    print("Finance App with MySQL is running!")
    print("Open: http://127.0.0.1:8000")
    print("="*50)
    uvicorn.run(app, host="127.0.0.1", port=8000)