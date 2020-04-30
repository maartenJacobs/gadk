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

The `on` method of your workflow instance can be used to specify when to run the workflow.
Currently `gadk` supports triggering a workflow on a pull request or a push/merge. Each
event can be limited to changes to files or directories, and when pushing to a branch.
See the `On` class for both options.

```python
from gadk import *


class MyWorkflow(Workflow):
    def __init__(self) -> None:
        super().__init__("my_workflow", "my workflow")

        # Run when:
        #   * for pull requests, a file under `src/` changes,
        #   * for merge/push to master.
        self.on(pull_request=On(paths=["src/**"]), push=On(branches=["master"]))
```

Note that it's mandatory to specify the `on` section of a workflow. This is not currently
being validated by `gadk.`

#### Adding jobs

The `self.jobs` property of your workflow instance can be used to add jobs to your workflow.
Each job must be an instance of `Job` or a subclass thereof.

A job has several options to specify:

* When to run the job: `Job(condition="..."")` specifies the condition on which to run the
job. For instance, `"github.ref == 'refs/heads/master'"` would only run the job when the
current branch is master. By default this condition is empty to always run the job.
* Which container to run the job on: `Job(runs_on="...")` specifies the name of the container.
By default this is `ubuntu-18.04`.
* Which steps to run: `Job(steps=[...])` specifies the steps to execute for this job.
Each step must be a `RunStep` or `UsesStep` instance or subclass thereof. By default `gadk`
adds a checkout v2 step and prepends it to the list of steps. This is a useful
default for most jobs but can be disabled by specifying `Job(default_checkout=False)`.
* Which environment variables to expose to the steps of the job: `Job(env={...})` specifies
additional environment variables. By default no environment variables are specified.
* Which jobs need to run before this job: `Job(needs=[...])` specifies the names of the jobs
that should run before this job. Leaving this list empty or unspecified means the job will
always run, which is also the default.

```python
from gadk import *


class MyWorkflow(Workflow):
    def __init__(self) -> None:
        super().__init__("my_workflow", "my workflow")

        # Specify 2 jobs to be run, one after the other..
        self.jobs["test"] = Job(
            steps=[RunStep("pytest"), RunStep("mypy")],  # Run 2 shell commands, one after the other.
            # condition=""  # No condition specified to run always.
            # runs_on="ubuntu-18.04"  # Run on the default container as specified by gadk.
            env={"PYTHONPATH": "."},  # Add 1 additional environment variable.
            # needs=None  # No other jobs need to be executed before this job.
            # default_checkout=True   # Prepend an additional step to checkout the repository.
        )
        self.jobs["build"] = Job(
            needs=["test"],  # The "test" job specified above must have finished running before this job can start.
            steps=[RunStep("tar ...")], # Run a single fictional command (excluding the default checkout command).
        )
```

#### Artifacts

Artifacts are files or directories created as a result of a job. They are typically used to share resources
between jobs, for instance when building code for deployment and verifying the code artifact before deployment,
and finally deploying said artifact. They can also be used for debugging, as Github Actions expose the artifacts
created by a workflow.

The default implementation of artifacts uses the `actions/upload-artifact@v2` action to upload an artifact
in one job and then uses the `actions/download-artifact@v2` action to download the artifact in a downstream
job.

`gadk` provides a simple abstraction of artifacts called `Artifact`. To use it you create an artifact
outside of your jobs, then add `artifact.as_upload()` to the steps of the job creating the artifact,
and finally add `artifact.as_download()` to the steps of the job(s) requiring the artifact.

```python
from gadk import *


class MyWorkflow(Workflow):
    def __init__(self) -> None:
        super().__init__("my_workflow", "my workflow")

        # Create a code archive as an artifact.
        code = Artifact(name="code-archive", path="build/code.zip")

        # Specify 2 jobs to be run in parallel.
        self.jobs["build"] = Job(
            steps=[
                # Build code archive somehow:
                RunStep("build_code_archive"),
                # Send off the archive for others to use.
                code.as_upload(),
            ]
        )
        self.jobs["verify"] = Job(
            needs=["build"],  # Needed to ensure the artifact is ready.
            steps=[
                # Get the artifact.
                code.as_download(),
                # Use somehow...
            ],
        )
```

## Roadmap

* Feature completeness: the first version of `gadk` was created to scratch a limited itch.
The next step is to represent all possible workflows.
* Validation: the configuration is not validated but elements like `workflow.on` are required.
In the future this could be validated using a Yaml schema validator and runtime checks, e.g. specifying
a non-existent job in `job.needs`.
