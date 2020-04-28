# GADK: codify Github Actions Workflows

[![PyPI version](https://badge.fury.io/py/gadk.svg)](https://badge.fury.io/py/gadk)

The extremely unofficial Github Actions Development Kit.

GADK can be used to:

* Define Github Actions Workflows as Python code and sync them to `.github/workflows/`.
* Share common Workflow patterns such as build-test-deploy.
* Abstract features like Artifacts.

`gadk` mirrors the options supported by Github Actions Workflows so that you can generate
workflows from Python code. The classes exported from the `gadk` module
should be sufficient to replicate existing workflows, with the additional advantage of
using Python's mechanisms of abstraction.

## Installation

GADK can be installed using `pip`.

```shell script
pip install gadk
```

## Instructions

### Setup

1. Create a file called `actions.py` in the root directory of your project.
1. Enter the following simple workflow with import:
    ```python
    from gadk import *


    class MyWorkflow(Workflow):
        def __init__(self) -> None:
            super().__init__("my_workflow", "my workflow")

            self.on(pull_request=On(paths=["src/**"]), push=On(branches=["master"]))
            self.jobs["test"] = Job(
                steps=[
                    RunStep("make test"),
                ],
            )
    ```
1. Run `gadk`.
1. You should now have a file called `.github/workflows/my_workflow.yml` with the contents
of your workflow.

### Creating workflows

Creating workflows starts with the `Workflow` class.

The `Workflow` class is the top-level element to represent a Github Action Workflow. You would
create a new class that extends `Workflow` when you are creating a new GADK project, or want to
test/deploy a new service or subproject. In the constructor of this new class you would specify
when the workflow is triggered, its jobs, the required environment variables, etc.

When initialising the `Workflow` class, you are required to specify a short name that is also
used as the filename in `.github/workflows/`. Additionally you may add a human-readable name.

#### When to run the workflow

Explain `self.on` and `On` class.

#### Adding jobs

Explain `self.jobs` and `Job` class.

#### Expressions

Explain Github expressions and `Expression` class.

#### Environment variables

Explain `EnvVars` type alias.

#### Artifacts

Explain usage and `Artifacts` shortcut.

## Roadmap

* Feature completeness: the first version of `gadk` was created to scratch a limited itch.
The next step is to represent all possible workflows.
* Validation: the configuration is not validated but elements like `workflow.on` are required.
In the future this could be validated using a Yaml schema validator and runtime checks, e.g. specifying
a non-existent job in `job.needs`.
