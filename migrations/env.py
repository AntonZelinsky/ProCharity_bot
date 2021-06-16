from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic.config import Config
from alembic import context
from app.config import Config as app_conf
from app.models import Base

alembic_cfg = Config()
config = context.config
fileConfig(config.config_file_name)

# Metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    ini_section = config.get_section(config.config_ini_section)

    db_path = app_conf.SQL_ALCHEMY_DATABASE_URL
    if db_path:
        ini_section['sqlalchemy.url'] = db_path

    connectable = engine_from_config(
        ini_section,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
