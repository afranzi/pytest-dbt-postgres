from dbt.cli.main import dbtRunner, dbtRunnerResult


class DbtExecutor:
    def __init__(self, dbt_project_dir: str, profiles_dir: str) -> None:
        self.dbt_project_dir = dbt_project_dir
        self.profiles_dir = profiles_dir

    def execute(self, command: str, params: list | None = None) -> dbtRunnerResult:
        dbt = dbtRunner()
        params = params or []
        invoke_command = [
            command,
            "--project-dir",
            self.dbt_project_dir,
            "--profiles-dir",
            self.profiles_dir,
        ]
        return dbt.invoke(invoke_command + params)
