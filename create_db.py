from app.shared.database import init_db

if __name__ == "__main__":
    print("Создание таблиц в базе данных...")
    init_db()
    print("Готово! Таблицы созданы успешно.")