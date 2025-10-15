import os
from sqlalchemy import create_engine, text

# Get database credentials from environment variables
user = os.getenv("user")
password = os.getenv("password")
db_name = os.getenv("db_name")


def get_engine():
    """
    Creates a SQLAlchemy engine using the standard connection string.
    
    Parameters:
        None
    
    Returns:
        engine: SQLAlchemy engine instance
    """
    connectionStr = f'postgresql+psycopg2://{user}:{password}@postgres:5432/{db_name}'
    engine = create_engine(connectionStr)
    return engine


def check_table_exists(table_name: str, schema: str) -> bool:
    """
    Checks if a table or view exists in the public schema.
    
    Parameters:
        table_name: Name of the table or view to check
        schema: Schema name (e.g., 'bronze', 'silver', 'gold')
    
    Returns:
        exists: True if the table/view exists, False otherwise
    """
    query = text(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = :schema
            AND table_name = :table_name
        )
        """
    )
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(query, {"schema": schema, "table_name": table_name}).scalar()
        return bool(result)


def check_table_has_data(table_name: str, schema: str) -> bool:
    """Check if the table/view has at least one row."""
    query = text(f"SELECT 1 FROM {schema}.{table_name} LIMIT 1")
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(query).first()
        return result is not None
