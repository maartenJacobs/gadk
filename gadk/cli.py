import importlib
from os import getcwd
from typing import Any, List, Type

import click
import sys

from gadk import Workflow


def output_to_file(workflow_out: str):
    pass


def output_to_stdout(workflow_out: str):
    print(workflow_out)


def workflows_from_module(actions: Any) -> List[Workflow]:
    """
    Extract workflows from imported module.

    Typing is mostly disabled for this function because:
        1. Workflow subclasses are expected. If they are not present, `gadk` can do no work.
        2. Workflow subclasses should define a constructor with no arguments. The arguments
           exist for the programmer to name the workflow. `gadk` cannot guess these arguments.
    """
    subclasses = actions.Workflow.__subclasses__()  # type: ignore
    workflows: List[Workflow] = [workflow() for workflow in subclasses]  # type: ignore
    return workflows


@click.command(context_settings={"help_option_names": ["-h", "--help"]},)
@click.option(
    "--print/--no-print",
    default=False,
    help="Print workflow YAML to stdout. By default each workflow is written to .github/workflows/.",
)
def cmd(print: bool):
    """Generate Github Actions workflows from code."""

    # Import actions.py from the current working directory.
    sys.path.insert(0, getcwd())
    actions = importlib.import_module("actions")
    sys.path.pop(0)

    # Determine output per workflow.
    outputter = output_to_stdout if print else output_to_file

    # Assume actions.py imports all elements of gadk to get subclasses of Workflow.
    for workflow in workflows_from_module(actions):
        outputter(workflow.render())


if __name__ == "__main__":
    cmd()
