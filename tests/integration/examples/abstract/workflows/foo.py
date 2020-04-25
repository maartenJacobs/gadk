from .lib import Service


class FooService(Service):
    def __init__(self) -> None:
        super().__init__("foo")

    def service_name(self) -> str:
        return "foo"
