---
title: TIL - An implicit context registration pattern in Python
posted_on: 2025-08-23
last_update: 2025-08-23
draft: false
abstract: >
    A neat pattern in Python: using context managers and a stack to implicitly register objects to their parent—without explicit wiring.
---

```note
This post is part of a "Today I Learned" series, which is meant to collect small
things I've learned that I found useful enough to publish. Very much inspired
by [Simon Willison's TIL blog](https://til.simonwillison.net/).

In the future, this may be spun off into another category separate from my longer posts.
```

Attaching related objects together is a common task in Python libraries. For example, you might want a dashboard to keep track of tables and graphs you create in your code.

There are several ways to do this, ranging from explicit assignments to more "magical" approaches.

## Explicit assignment

If you don't care about mutating objects (in most cases, you should), it is perfectly valid to write:

```python
import polars as pl
from matplotlib import pyplot as plt

from lib import Dashboard

dash = Dashboard()

dash.tables = [pl.read_csv("...")]

fig, ax = plt.subplots()
# do stuff

dash.graphs = [fig]
```

Then, if you want some additional behavior to kick in upon mutating these objects, you will want to define some kind of **setter method**, which you would call like:

```python
dash = Dashboard()
dash.add_table(...)
dash.add_graph(...)
```

## The builder pattern

Another way is to equip your `Dashboard` to work with **the builder pattern**, which is cleaner as it avoids mutating the dashboard altogether. Instead, we build said object in a single assignment.

```python
import polars as pl
from matplotlib import pyplot as plt

from lib import Dashboard

fig, ax = plt.subplots()
# do stuff

dash = (
    Dashboard()
    .add_table(pl.read_csv("..."), label="Base table")
    .add_graph(fig, label="Base graph")
)
```

This can however become difficult to read and could require quite a few intermediate variables to set it up, especially if the table and graph definitions span multiple lines.

## The implicit registration pattern

There is a third way you may be interested in if you're not afraid of adding a bit of a magic in your API.

Look at the piece of code below:

```python
from lib import Dashboard, Table, Graph

with Dashboard() as dash:
    table = Table(pl.read_csv("..."), label="Base table")
    other_table = Table(table.df.pipe(some_func), label="Derived table")

    fig, ax = plt.subplots()
    # do stuff
    graph = Graph(fig, label="Base graph")

print(dash.tables) 
# [<lib.Table object at 0x107528830>, <lib.Table object at 0x1063ca0d0>]

print(dash.graphs) 
# [<lib.Graph object at 0x10752bb60>]
```

We "magically" bound `table` and `graph` to `dash` without having to do anything but define objects in a context manager.

This is quite elegant, especially when the code for building those tables and graphs spans many lines.

This was done using a **stack** of references to instances stored on the `Dashboard` class, like so:

```python
class Dashboard:
    instances: list["Dashboard"] = []
    tables: list["Table"]
    graphs: list["Graph"]

    def __init__(self) -> None:
        self.tables = []
        self.graphs = []

    def __enter__(self):
        self.__class__.instances.append(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__class__.instances.pop()


class Table:
    def __init__(self, df: pl.DataFrame, label: str) -> None:
        self.df = df
        self.label = label

        if Dashboard.instances:
            parent = Dashboard.instances[-1]
            parent.tables.append(self)


class Graph:
    def __init__(self, fig: Figure, label: str) -> None:
        self.fig = fig
        self.label = label

        if Dashboard.instances:
            parent = Dashboard.instances[-1]
            parent.graphs.append(self)
```

Upon entering the [context manager](https://peps.python.org/pep-0343/), the `__enter__` method is called, and the dashboard instance is pushed on the `Dashboard.instances` stack.

Then, whenever we create a `Table` or `Graph` instance, we grab the top of the stack, and bind said table or graph to that dashboard instance.

Finally, when we exit the context, we pop the dashboard instance off the stack.

This setup can also handle nested structures. Imagine our dashboard can also include sub-dashboards, e.g. in a multi-page setup.

We can make it so dashboards can bind to dashboards, i.e.

```python
class Dashboard:
    instances: list["Dashboard"] = []
    tables: list["Table"]
    graphs: list["Graph"]
    dashboards: list["Dashboard"]

    def __init__(self) -> None:
        self.tables = []
        self.graphs = []
        self.dashboards = []

        if Dashboard.instances:
            parent = Dashboard.instances[-1]
            parent.dashboards.append(self)     
```

And now we can write things like:

```python
with Dashboard() as dash:
    table = Table(pl.read_csv("..."), label="Base table")
    other_table = Table(table.df.pipe(some_func), label="Derived table")

    fig, ax = plt.subplots()
    # do stuff

    graph = Graph(fig, label="Base graph")

    with Dashboard():
        table = Table(pl.read_csv("..."), label="Another base table")

print(dash.dashboards)

# [<lib.Dashboard object at 0x1269f9a90>]
```

Another use case for this pattern is to build tree-like structures gradually, since the indentation and scopes created by context managers mimic these tree structures quite well visually.

For example, if you need to match a folder structure specification with an actual folder on your machine, you could:

```python
from lib import Folder

# Write a spec like this:
with Folder(name="root") as spec:
    File(name="A.xlsx")
    File(name="B.json")
    
    with Folder(name="subfolder"):
        File(name="C.txt")

# And validate like this:
path_to_folder = ...
spec.validate_against(path_to_folder)
```

This pattern is used by the probabilistic programming library [PyMC](https://www.pymc.io/welcome.html) (formerly PyMC3), which uses it for scoping model definitions (see this [example](https://www.pymc.io/projects/docs/en/stable/learn/core_notebooks/GLM_linear.html#estimating-the-model)).