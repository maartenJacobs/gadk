# GADK

The extremely unofficial Github Actions Development Kit.

## Example

Below is a very simple example of generating a Workflow file. Take it with a grain of salt.
GADK only shines when there are more workflows that look similar or share configuration.

Create a file called actions.py:

```python3
from gadk import *


class MyService(Workflow):
    def __init__(self) -> None:
        super().__init__("my_service", "my service workflow")

        paths = [
            "src/service/*.py",
            "src/service.yml",
        ]
        self.on(
            pull_request=On(paths=paths), push=On(branches=["master"], paths=paths),
        )

        self.jobs["test"] = Job(
            steps=[
                RunStep("make build"),
                RunStep("make lint"),
                RunStep("make test"),
            ],
        )
```

Run `python gadk/cli.py`. You should see the following printed (soon to be written to a file):

```yaml
name: my service workflow
'on':
  pull_request:
    paths:
    - src/service/*.py
    - src/service.yml
  push:
    paths:
    - src/service/*.py
    - src/service.yml
    branches:
    - master
jobs:
  test:
    runs-on: ubuntu-18.04
    steps:
    - uses: actions/checkout@v1
    - run: make build
    - run: make lint
    - run: make test
```
