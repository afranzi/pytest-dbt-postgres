import os
import unittest

from pytest_dbt_postgres import auto_inject_fixtures
from pytest_dbt_postgres.dbt_executor import DbtExecutor
from pytest_dbt_postgres.dbt_validator import DbtValidator
from pytest_dbt_postgres.postgres.connector import PostgresConnector
from pytest_dbt_postgres.postgres.sql_methods import (
    export_credentials_to_env,
    get_credentials,
)

dbt_project_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "dummy_gummy"),
)
resources_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources"))


@auto_inject_fixtures("postgresql")
class TestDbtValidator(unittest.TestCase):
    def setUp(self) -> None:
        credentials = get_credentials(self.postgresql)
        self.connector = PostgresConnector(credentials)

        # SETUP
        export_credentials_to_env(credentials)
        executor = DbtExecutor(
            dbt_project_dir=dbt_project_dir,
            profiles_dir=resources_folder,
        )
        self.validator = DbtValidator(
            connector=self.connector,
            executor=executor,
            resources_folder=resources_folder,
        )

    def test_orders(self) -> None:
        # GIVEN
        sources_to_load = [
            ("external.customers", "csv/input/customers.csv"),
            ("external.orders", "csv/input/orders.csv"),
        ]
        selector = "orders"
        outputs_to_validate = [
            ("dbt_unittest.orders", "csv/output/orders.csv"),
        ]

        self.validator.validate(sources_to_load, selector, outputs_to_validate)
