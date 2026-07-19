# saarthiIQ-Backend\alembic\env.py
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Safely resolve the database url using internal configurations or direct fallback
database_url = None

try:
    from app.core.config import settings
    database_url = getattr(settings, "DATABASE_URL", None)
except ImportError:
    try:
        from app.config import settings
        database_url = getattr(settings, "DATABASE_URL", None)
    except ImportError:
        pass

# If no internal settings exist, check environment variables or use local Postgres default
if not database_url:
    from dotenv import load_dotenv
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/saarthiiq")

import app.models.user
import app.models.session
import app.models.candidate
import app.models.campaign
import app.models.interview
import app.models.task
import app.models.note
import app.models.resume
import app.models.audit
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    
# 2. Inject the extracted string directly
config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
