from gadk import *


class MyService(Workflow):
    def __init__(self) -> None:
        super().__init__("my_service", "my service workflow")

        paths = [
            "src/service/*.py",
            "src/service.yml",
        ]
        self.on(
            pull_request=On(paths=paths), push=On(branches=["master"], paths=paths),
        )

        self.jobs["test"] = Job(
            steps=[
                RunStep("make build"),
                RunStep("make lint"),
                RunStep("make test"),
            ],
        )