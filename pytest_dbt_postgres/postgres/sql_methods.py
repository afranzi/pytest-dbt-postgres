import os

from dbt.contracts.graph.nodes import ColumnInfo
from psycopg import Connection

from pytest_dbt_postgres.postgres.connector import PostgresConnector
from pytest_dbt_postgres.postgres.credentials import DatabaseCredentials


def get_credentials(postgres_connection: Connection) -> DatabaseCredentials:
    return DatabaseCredentials(
        driver_name="postgresql+psycopg2",
        host=postgres_connection.info.host,
        user=postgres_connection.info.user,
        password=postgres_connection.info.password,
        database=postgres_connection.info.dbname,
        port=postgres_connection.info.port,
    )


def export_credentials_to_env(credentials: DatabaseCredentials) -> None:
    for key, value in credentials.dict().items():
        os.environ[f"DBT_POSTGRES_TEST_{key.upper()}"] = str(value)


def create_role(connector: PostgresConnector, role: str) -> None:
    query = f"""
        DO
        $do$
        BEGIN
           IF EXISTS (
              SELECT FROM pg_catalog.pg_roles
              WHERE  rolname = '{role}') THEN
              RAISE NOTICE 'Role "{role}" already exists. Skipping.';
           ELSE
              CREATE ROLE {role};
           END IF;
        END
        $do$;
    """
    connector.execute(query)


def create_schema(connector: PostgresConnector, schema: str) -> None:
    connector.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")


def create_table(
    connector: PostgresConnector,
    schema: str,
    table: str,
    columns: list[ColumnInfo],
) -> None:
    columns = [f"{column.name} {column.data_type}" for column in columns]
    columns = ",".join(columns)
    ddl = f"CREATE TABLE IF NOT EXISTS {schema}.{table} ({columns})"
    connector.execute(ddl)
