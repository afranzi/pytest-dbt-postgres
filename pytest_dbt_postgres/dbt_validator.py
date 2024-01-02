import os

import numpy as np
import pandas as pd
from dbt.cli.main import dbtRunnerResult
from dbt.contracts.graph.nodes import SourceDefinition
from dbt.contracts.results import TestStatus
from pandas.testing import assert_frame_equal

from pytest_dbt_postgres.dbt_executor import DbtExecutor
from pytest_dbt_postgres.postgres.connector import PostgresConnector
from pytest_dbt_postgres.postgres.sql_methods import create_schema, create_table


class DbtExecException(Exception):
    pass


class DbtValidator:
    def __init__(
        self,
        connector: PostgresConnector,
        executor: DbtExecutor,
        resources_folder: str,
    ) -> None:
        self.connector = connector
        self.executor = executor
        self.resources_folder = resources_folder

        # Initialize validator
        parse_res = self.executor.execute(command="parse")
        self.sources = self.dbt_create_sources(parse_res)

    def dbt_load_source(self, source: str, csv_source_file: str) -> None:
        file = os.path.join(self.resources_folder, csv_source_file)
        source_definition = self.sources[source]
        copy_sql_query = f"""
            COPY {source}({','.join(source_definition.columns.keys())})
            FROM '{file}'
            DELIMITER ','
            CSV HEADER;
        """
        self.connector.execute(copy_sql_query)

    def dbt_load_sources(self, sources_to_load: list[tuple[str, str]]) -> None:
        # STEP 1: Populate Source Tables with CSV/JSON files
        for source, csv_source_file in sources_to_load:
            self.dbt_load_source(source, csv_source_file)

    def dbt_create_sources(self, res: dbtRunnerResult) -> dict[str, SourceDefinition]:
        sources: list[SourceDefinition] = [  # type: ignore
            source for source in res.result.sources.values() if source.columns
        ]

        for source in sources:
            create_schema(self.connector, source.schema)
            create_table(
                self.connector,
                source.schema,
                source.name,
                list(source.columns.values()),
            )

        return {f"{source.schema}.{source.name}": source for source in sources}

    @staticmethod
    def validate_dbt_exec_result(res: dbtRunnerResult) -> None:
        errors = (
            result for result in res.result.results if result and result.status in [TestStatus.Fail, TestStatus.Error]
        )
        for error in errors:
            raise DbtExecException(f"Issue in {error.node.name} - {error.message}")

    def execute_dbt(self, selector: str, quiet: bool = True) -> None:
        quiet_param = "-q" if quiet else ""

        # STEP 2A: Execute [seed|run|test] jobs
        self.executor.execute(
            command="seed",
            params=["--select", f"@{selector}", quiet_param],
        )
        run_res = self.executor.execute(
            command="run",
            params=["--select", f"@{selector}", quiet_param],
        )
        test_res = self.executor.execute(
            command="test",
            params=["--select", selector, quiet_param],
        )

        # STEP 2B: Fail if dbt [run|test] fails
        self.validate_dbt_exec_result(run_res)
        self.validate_dbt_exec_result(test_res)

    def dbt_validate_output(self, table: str, csv_output_file: str) -> None:
        output = self.connector.fetch_data(f"SELECT * FROM {table}")
        df = pd.DataFrame.from_records(output).astype(str).transform(np.sort)

        expected_file_path = os.path.join(self.resources_folder, csv_output_file)
        expected_df = pd.read_csv(expected_file_path, header=0, dtype=str).transform(
            np.sort,
        )
        assert_frame_equal(df, expected_df)

    def dbt_validate_outputs(self, outputs_to_validate: list[tuple[str, str]]) -> None:
        # STEP 3: Validate Output Tables versus CSV files
        for table, csv_output_file in outputs_to_validate:
            self.dbt_validate_output(table, csv_output_file)

    def validate(
        self,
        sources_to_load: list[tuple[str, str]],
        selector: str,
        outputs_to_validate: list[tuple[str, str]],
    ) -> None:
        # STEP 1: Populate Source Tables with CSV/JSON files
        self.dbt_load_sources(sources_to_load)

        # STEP 2: Execute [seed|run|test] jobs & fail if execution errors
        self.execute_dbt(selector)

        # STEP 3: Validate Output Tables versus CSV files
        self.dbt_validate_outputs(outputs_to_validate)
