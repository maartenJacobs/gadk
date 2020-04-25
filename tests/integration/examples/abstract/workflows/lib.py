from gadk import *

from abc import ABC


class Service(Workflow, ABC):
    def __init__(self, filename: str) -> None:
        name = self.service_name()
        super().__init__(filename, f"{name} service")

        self.jobs["test"] = Job(
            steps=[
                RunStep(f"make name=\"{name}\" build"),
                RunStep(f"make name=\"{name}\" test"),
            ],
        )

    @abstractmethod
    def service_name(self) -> str:
        pass
