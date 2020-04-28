# 0.1.2

* Generated files now start with a comment to prevent manual modification.

# 0.1.1

* Abstractions of workflows are now supported:
  ```python
  class BaseService(Workflow, ABC):
     @abstractmethod
     def concrete_data(self):
        pass

  class ServiceA(BaseService):
    pass
  ```
  In the example above, `ServiceA` will be detected as a workflow.
  `BaseService` will not be rendered as expected; only concrete workflows
  are rendered.
* The `workflow.on.branches` is now rendered before `workflow.on.paths`.

# 0.1.0

* Initial release.
* Basic features of workflows supported.
* `Artifact` abstraction included.
