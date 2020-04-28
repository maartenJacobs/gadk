from gadk import *


class MyService(Workflow):
    def __init__(self) -> None:
        super().__init__("my_service", "my service workflow")

        code_artifact = Artifact(name="code-archive", path="build/code.zip")

        self.jobs["build"] = Job(
            steps=[RunStep("make build"), code_artifact.as_upload(),],
        )
        self.jobs["deploy"] = Job(
            steps=[code_artifact.as_download(), RunStep(f"scp {code_artifact.path}")],
        )
