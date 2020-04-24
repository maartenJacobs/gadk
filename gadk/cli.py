import importlib

import click
import sys


@click.command()
def cmd():
    # Import actions.py from the current working directory.
    sys.path.append(".")
    actions = importlib.import_module("actions")

    # Assume actions.py imports all elements of gadk to get subclasses of Workflow.
    for workflow_class in actions.Workflow.__subclasses__():
        workflow_class().render()


if __name__ == "__main__":
    cmd()
