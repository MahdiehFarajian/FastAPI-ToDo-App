import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from core.database import Base
from pathlib import Path
from dotenv import load_dotenv
from configparser import ConfigParser, ExtendedInterpolation, BasicInterpolation

# Get the Alembic Config object
config = context.config

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print("Warning: .env file not found. Falling back to global environment variables.")

# Get DB URL
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Disable interpolation by replacing the file_config with a non-interpolating version
if config.file_config is not None:
    # Create a new parser with no interpolation
    new_parser = ConfigParser(interpolation=None)
    new_parser.read(config.config_file_name)
    config.file_config = new_parser

# Set SQLAlchemy DB URL into Alembic config
if SQLALCHEMY_DATABASE_URL:
    config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
else:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set in the environment variables.")

# Metadata for 'autogenerate'
from models import *
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=False, 
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=False,  
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
