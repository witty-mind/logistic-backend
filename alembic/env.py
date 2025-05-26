from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from pathlib import Path # Add this import
from dotenv import load_dotenv # Add this import
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env') # Modified this import

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.db.base import Base  # Add this import
from app.core.config import settings # Add this import

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Modified line

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url") # Original line
    url = settings.DATABASE_URL # Modified line
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config( # Original lines
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    
    # New connectable using settings
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )


    async with connectable.connect() as connection:
        # context.configure( # Original line
        #     connection=connection, target_metadata=target_metadata
        # )

        # with context.begin_transaction(): # Original line
        #     context.run_migrations()
        await connection.run_sync(do_run_migrations) # Modified to run in async way

    await connectable.dispose() # Dispose engine


# if context.is_offline_mode(): # Original lines
#     run_migrations_offline()
# else:
#     run_migrations_online()

# New async execution
import asyncio

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
