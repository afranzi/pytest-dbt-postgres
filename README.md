# PyTest DBT Postgres

This project aims to provide an easy way to validate a DBT project by enabling the
unit-testing capability.

## Dependencies

This project is based on the [pytest-postgresql](https://pypi.org/project/pytest-postgresql/) library, so we can
validate our DBT postgres project without relying on an existing database.

## Usage

The initial idea resides on pytest-postgres providing us an empty and isolated postgres where we can
validate different use-cases with our DBT code.

> If your project uses external sources, you will need to make sure they are properly defined in the yml files, since
> the project generates the DDLs from there.

```python
import unittest

from pytest_dbt_postgres import auto_inject_fixtures
from pytest_dbt_postgres.dbt_executor import DbtExecutor
from pytest_dbt_postgres.dbt_validator import DbtValidator
from pytest_dbt_postgres.postgres.connector import PostgresConnector
from pytest_dbt_postgres.postgres.sql_methods import export_credentials_to_env, get_credentials

dbt_project_dir = '...'
resources_folder = '...'


@auto_inject_fixtures("postgresql")
class TestDbtValidator(unittest.TestCase):
    def setUp(self) -> None:
        credentials = get_credentials(self.postgresql)
        self.connector = PostgresConnector(credentials)

        # SETUP
        export_credentials_to_env(credentials)
        executor = DbtExecutor(dbt_project_dir=dbt_project_dir, profiles_dir=resources_folder)
        self.validator = DbtValidator(connector=self.connector, executor=executor, resources_folder=resources_folder)

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
        # THEN
        self.validator.validate(sources_to_load, selector, outputs_to_validate)
```
