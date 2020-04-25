from .lib import Service


class BarService(Service):
    def __init__(self) -> None:
        super().__init__("bar")

    def service_name(self) -> str:
        return "bar"


