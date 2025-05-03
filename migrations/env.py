from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Добавляем корень проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем все модели
from app.shared.database import Base
from app.shared.models.user import User
from app.shared.models.team import Team, TeamMember
from app.shared.models.task import Task, TaskAssignment

# Получаем конфиг из alembic.ini
config = context.config

# Настраиваем логгирование
fileConfig(config.config_file_name)

# Указываем целевую метаданную
target_metadata = Base.metadata

def run_migrations_online():
    """Запуск миграций в онлайн-режиме"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()