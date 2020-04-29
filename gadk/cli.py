import importlib
import inspect
from os import getcwd, makedirs
from os.path import exists
from typing import List, Set, Optional

import click
import sys

from gadk import Workflow


def output_to_file(workflow: Workflow):
    """Write the workflow to .github/workflows/{workflow.filename}.yml."""

    makedirs(".github/workflows/", exist_ok=True)
    with open(f".github/workflows/{workflow.filename}.yml", mode="w") as fd:
        fd.write(workflow.render())


def output_to_stdout(workflow: Workflow):
    click.echo(workflow.render())


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


def import_workflows():
    # Import actions.py from the current working directory.
    sys.path.insert(0, getcwd())
    importlib.import_module("actions")
    sys.path.pop(0)

    # Sort workflows for consistency.
    return sorted(find_workflows(), key=lambda w: w.name)


def fetch_actual_workflow_contents(workflow_name: str) -> Optional[str]:
    workflow_path = f".github/workflows/{workflow_name}.yml"
    if not exists(workflow_path):
        return None
    else:
        with open(f".github/workflows/{workflow_name}.yml") as fd:
            return fd.read()


def _sync(print_to_stdout: bool):
    # Determine output per workflow.
    outputter = output_to_stdout if print_to_stdout else output_to_file

    # Assume actions.py imports all elements of gadk to get subclasses of Workflow.
    workflows = import_workflows()
    for workflow in workflows:
        outputter(workflow)


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
@click.option(
    "--print/--no-print",
    default=False,
    help="Print workflow YAML to stdout. By default each workflow is written to .github/workflows/.",
)
@click.version_option()
def cmd(ctx: click.Context, print: bool = False):
    """Generate Github Actions workflows from code."""
    if ctx.invoked_subcommand is None:
        _sync(print)


@cmd.command()
@click.option(
    "--print/--no-print",
    default=False,
    help="Print workflow YAML to stdout. By default each workflow is written to .github/workflows/.",
)
def sync(print: bool):
    """Generate Github Actions workflows from code."""
    _sync(print)


@cmd.command()
def check():
    """Check if generated workflow files are up to date."""
    success = True
    for workflow in import_workflows():
        actual_content = fetch_actual_workflow_contents(workflow.filename)
        if actual_content is None or actual_content != workflow.render():
            click.echo(
                click.style(f"Workflow {workflow.filename} is outdated!", fg="red")
            )
            success = False
        else:
            click.echo(f"Workflow {workflow.filename} is up to date.")

    if not success:
        raise click.exceptions.ClickException(
            "Some workflows are outdated. Please run gadk to sync workflows."
        )


if __name__ == "__main__":
    cmd()
