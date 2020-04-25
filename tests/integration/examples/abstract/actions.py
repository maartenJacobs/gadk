"""
Example of using a service superclass to abstract workflow patterns.
The abstracted workflow patterns would no longer need to live in a single file,
making it easier for monorepos to add and register workflows dynamically.

Only FooService and BarService are expected to be output. `Service` could be located
anywhere.
"""

from workflows import *  # noqa
