from abc import abstractmethod, ABC
from typing import Any, Dict, Optional, Iterable, List, Union

import yaml

from .constants import *


class Yamlable(ABC):
    @abstractmethod
    def to_yaml(self) -> Any:
        """Return a representation of the object that can be rendered as YAML."""


class Expression(Yamlable):
    def __init__(self, expr: str) -> None:
        super().__init__()
        self._expr = expr

    def to_yaml(self) -> Any:
        return "${{ %s }}" % self._expr


EnvVars = Dict[str, Union[Any, Expression]]


class On(Yamlable):
    def __init__(
        self,
        paths: Optional[Iterable[str]] = None,
        branches: Optional[Iterable[str]] = None,
    ) -> None:
        super().__init__()
        self._paths = paths or []
        self._branches = branches or []

    def to_yaml(self) -> Any:
        on = {}
        if self._paths:
            on["paths"] = list(self._paths)
        if self._branches:
            on["branches"] = list(self._branches)
        return on


class Step(Yamlable, ABC):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        condition: str = "",
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self._name: Optional[str] = name
        self._env: Dict[str, str] = env or {}
        self._if: str = condition or ""
        # TODO: add later
        # self._id
        # self._continue_on_error
        # self._timeout_in_minutes

    def to_yaml(self) -> Any:
        step = {}
        if self._name:
            step["name"] = self._name
        if self._if:
            step["if"] = self._if
        return self.step_extension(step)

    @abstractmethod
    def step_extension(self, step: Dict) -> Dict:
        pass


class RunStep(Step):
    def __init__(
        self,
        cmd: str,
        name: Optional[str] = None,
        condition: str = "",
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(name=name, condition=condition, env=env)
        self._cmd: str = cmd

    def step_extension(self, step: Dict) -> Dict:
        step["run"] = self._cmd
        return step


class UsesStep(Step):
    def __init__(
        self,
        action: str,
        name: Optional[str] = None,
        condition: str = "",
        with_args: Optional[Dict] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(name=name, condition=condition, env=env)
        self._action = action
        self._with: Dict[str, str] = with_args or {}
        self._env: Dict[str, str] = env or {}

    def with_args(self, **kwargs):
        self._with = kwargs

    def step_extension(self, step: Dict) -> Dict:
        step["uses"] = self._action
        if self._with:
            step["with"] = self._with
        return step


class Artifact:
    """Abstraction for the download- and upload-artifact actions."""

    def __init__(self, *, name: str, path: str) -> None:
        super().__init__()
        self._name: str = name
        self._path: str = path

    def as_upload(self) -> UsesStep:
        return UsesStep(
            action=ACTION_UPLOAD, with_args={"name": self._name, "path": self._path,}
        )

    def as_download(self) -> UsesStep:
        return UsesStep(
            action=ACTION_DOWNLOAD, with_args={"name": self._name, "path": self._path,}
        )


class Job(Yamlable):
    def __init__(
        self,
        *,
        condition: str = "",
        runs_on: str = "ubuntu-18.04",
        steps: Optional[List[Step]] = None,
        needs: Optional[List[str]] = None,
        env: Optional[EnvVars] = None,
        default_checkout: bool = True,
    ) -> None:
        super().__init__()
        self._if: str = condition or ""
        self._runs_on: str = runs_on
        self._steps: List[Step] = steps or []
        self._needs: List[str] = needs or []
        self._env: EnvVars = env or {}
        if default_checkout:
            self._steps.insert(0, UsesStep(action=ACTION_CHECKOUT))

    def add_step(self, step: Step):
        self._steps.append(step)

    def to_yaml(self) -> Any:
        job = {}
        if self._if:
            job["if"] = self._if
        if self._needs:
            job["needs"] = self._needs
        job["runs-on"] = self._runs_on
        if self._env:
            from .utils import env_vars_to_yaml

            job["env"] = env_vars_to_yaml(self._env)
        if self._steps:
            job["steps"] = [step.to_yaml() for step in self._steps]
        return job


class Workflow(Yamlable):
    def __init__(self, filename: str, name: str) -> None:
        super().__init__()
        self._filename: str = filename
        self._name: str = name
        self._on: Dict[str, On] = {}
        self.jobs: Dict[str, Job] = {}

    def on(self, pull_request: Optional[On] = None, push: Optional[On] = None):
        if pull_request:
            self._on["pull_request"] = pull_request
        else:
            del self._on["pull_request"]
        if push:
            self._on["push"] = push
        else:
            del self._on["push"]

    def to_yaml(self) -> Any:
        workflow = {
            "name": self._name,
        }
        if self._on:
            workflow["on"] = {on_key: on.to_yaml() for on_key, on in self._on.items()}
        if self.jobs:
            workflow["jobs"] = {
                job_name: job.to_yaml() for job_name, job in self.jobs.items()
            }
        return workflow

    def render(self):
        print(yaml.safe_dump(self.to_yaml(), sort_keys=False))
