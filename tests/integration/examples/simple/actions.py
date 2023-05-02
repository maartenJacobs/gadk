from gadk import *


class MyService(Workflow):
    def __init__(self) -> None:
        super().__init__(
            "my_service",
            "my service workflow",
            concurrency_group='${{ github.workflow }}-${{ github.head_ref || github.run_id }}',
            cancel_in_progress=True,
        )

        paths = [
            "src/service/*.py",
            "src/service.yml",
        ]
        self.on(
            pull_request=On(paths=paths),
            push=On(branches=["master"], paths=paths),
            workflow_dispatch=Null(),
        )

        self.jobs["test"] = Job(
            steps=[RunStep("make build"), RunStep("make lint"), RunStep("make test"),],
        )
