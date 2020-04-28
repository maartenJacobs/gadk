from gadk import *


class MakeStep(RunStep):
    def __init__(
        self,
        make_cmd: str,
        *,
        cmd_args: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        cmd: str = f"make {make_cmd}"
        if cmd_args:
            args: str = " ".join(
                f'{arg_name}="{arg_value}"' for arg_name, arg_value in cmd_args.items()
            )
            cmd += f" {args}"
        super().__init__(cmd=cmd, name=name, env=env)


class FooBarService(Workflow):
    def __init__(self) -> None:
        super().__init__("foobar", "foobar service")

        self.jobs["test"] = Job(
            steps=[
                MakeStep("build"),
                MakeStep("lint", cmd_args={"verbose": "1"}),
                MakeStep("test", cmd_args={"verbose": "1", "suite": "unit"}),
            ]
        )
