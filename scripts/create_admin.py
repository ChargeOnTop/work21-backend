#!/usr/bin/env python3
"""
Скрипт для создания администратора
Использование: python scripts/create_admin.py
"""
import asyncio
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole


async def create_admin(email: str, password: str, first_name: str, last_name: str):
    """Создать администратора в базе данных"""
    
    # Инициализируем БД
    await init_db()
    
    async with async_session_maker() as session:
        # Проверяем, существует ли уже пользователь
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.role == UserRole.ADMIN:
                print(f"⚠️  Администратор с email {email} уже существует")
                return
            else:
                # Повышаем до админа
                existing_user.role = UserRole.ADMIN
                existing_user.is_active = True
                existing_user.is_verified = True
                await session.commit()
                print(f"✅ Пользователь {email} повышен до администратора")
                return
        
        # Создаём нового админа
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            rating_score=0.0,
            completed_projects=0,
        )
        
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        print(f"✅ Администратор создан:")
        print(f"   Email: {email}")
        print(f"   Имя: {first_name} {last_name}")
        print(f"   ID: {admin.id}")


def main():
    """Главная функция"""
    print("=" * 50)
    print("🔐 Создание администратора WORK21")
    print("=" * 50)
    
    # Данные по умолчанию или из аргументов
    if len(sys.argv) >= 5:
        email = sys.argv[1]
        password = sys.argv[2]
        first_name = sys.argv[3]
        last_name = sys.argv[4]
    else:
        # Интерактивный режим
        email = input("Email [admin@work21.ru]: ").strip() or "admin@work21.ru"
        password = input("Пароль [Admin123!]: ").strip() or "Admin123!"
        first_name = input("Имя [Admin]: ").strip() or "Admin"
        last_name = input("Фамилия [Work21]: ").strip() or "Work21"
    
    if len(password) < 8:
        print("❌ Пароль должен быть не менее 8 символов")
        sys.exit(1)
    
    asyncio.run(create_admin(email, password, first_name, last_name))
    
    print()
    print("🎉 Готово! Теперь вы можете войти в админ-панель:")
    print(f"   URL: http://localhost:3000/login")
    print(f"   Email: {email}")
    print(f"   Пароль: {password}")


if __name__ == "__main__":
    main()

