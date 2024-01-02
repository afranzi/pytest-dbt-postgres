from __future__ import annotations

from functools import cached_property

import psycopg2
from absl import logging
from psycopg2 import sql
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

from pytest_dbt_postgres.postgres.credentials import DatabaseCredentials


class PostgresConnector:
    def __init__(
        self,
        credentials: DatabaseCredentials,
        autocommit: bool = True,
    ) -> None:
        self.credentials = credentials
        self.autocommit = autocommit

    @cached_property
    def conn(self) -> connection:
        _conn = psycopg2.connect(
            host=self.credentials.host,
            user=self.credentials.user,
            password=self.credentials.password,
            database=self.credentials.database,
            port=self.credentials.port,
        )
        _conn.set_session(autocommit=self.autocommit)
        return _conn

    def execute(self, query: str) -> RealDictCursor:
        logging.info(f"Running query = {query}")
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL(query)
        cursor.execute(query)
        return cursor

    def fetch_data(self, query: str) -> list[dict]:
        cs = self.conn.cursor(cursor_factory=RealDictCursor)
        cs.execute(query)
        records = cs.fetchall()
        return [dict(row) for row in records]

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    def __exit__(
        self,
        exception_type: str,
        exception_value: str,
        traceback: str,
    ) -> None:
        self.conn.close()
        logging.info("Closing connection...")

    def __del__(self) -> None:
        self.conn.close()
        logging.info("Closing connection...")

    def __enter__(self) -> PostgresConnector:
        return self
