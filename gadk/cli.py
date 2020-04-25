import abc
import importlib
import inspect
from os import getcwd, makedirs
from typing import Any, List, Set

import click
import sys

from gadk import Workflow


def output_to_file(workflow: Workflow):
    """Write the workflow to .github/workflows/{workflow.filename}.yml."""

    makedirs(".github/workflows/", exist_ok=True)
    with open(f".github/workflows/{workflow.filename}.yml", mode="w") as fd:
        fd.write(workflow.render())


def output_to_stdout(workflow: Workflow):
    print(workflow.render())


def find_workflows() -> List[Workflow]:
    """
    Extract workflows from imported module.

    Typing is mostly disabled for this function because:
        1. Workflow subclasses are expected. If they are not present, `gadk` can do no work.
        2. Workflow subclasses should define a constructor with no arguments. The arguments
           exist for the programmer to name the workflow. `gadk` cannot guess these arguments.
    """

    def _find_workflows(subclasses: List, workflows: Set) -> Set:
        """
        Recursive function to find workflows by descending a class hierarchy of abstract workflows.

        Simple workflows will return immediately. More complex projects might recurse once or twice.
        """
        child_workflows = []
        for workflow_class in subclasses:
            # Add subclasses of abstract subclasses. This allows for further abstractions of workflows.
            if inspect.isabstract(workflow_class):
                child_workflows += [
                    child_workflow
                    for child_workflow in workflow_class.__subclasses__()
                    if child_workflow not in workflows
                ]
            else:
                workflows.add(workflow_class)

        if child_workflows:
            return _find_workflows(child_workflows, workflows)
        return workflows

    # Collect the workflows detected in the module. There may be abstractions of workflows,
    # so we'll look at subclasses of subclasses, and so on, if necessary.
    workflows = _find_workflows(Workflow.__subclasses__(), set())

    # Filter out those abstract workflows. Only concrete workflows should be returned.
    return [
        workflow_class()
        for workflow_class in workflows
        if not inspect.isabstract(workflow_class)
    ]


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--print/--no-print",
    default=False,
    help="Print workflow YAML to stdout. By default each workflow is written to .github/workflows/.",
)
def cmd(print: bool):
    """Generate Github Actions workflows from code."""

    # Import actions.py from the current working directory.
    sys.path.insert(0, getcwd())
    importlib.import_module("actions")
    sys.path.pop(0)

    # Determine output per workflow.
    outputter = output_to_stdout if print else output_to_file

    # Assume actions.py imports all elements of gadk to get subclasses of Workflow.
    # Sort workflows for consistency.
    workflows = sorted(find_workflows(), key=lambda w: w.name)
    for workflow in workflows:
        outputter(workflow)


if __name__ == "__main__":
    cmd()
