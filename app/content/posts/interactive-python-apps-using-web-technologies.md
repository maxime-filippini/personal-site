---
title: Interactive Python applications using Web technologies
posted_on: 2026-02-23
last_update: 2026-02-23
draft: true
abstract: >
    TBD
---

If you've been working in Python for a length of time, you may have heard of
tools like `dash`, `streamlit` and `gradio` that allow you to build interactive
data-centric applications, all in Python. These tools are interesting, have a
low barrier to entry, and are definitely worth exploring.

In this post however, we will go over the principles and concepts behind the
use of web technologies to power interactive Python-based applications. Based
on these principles, we will build a simple interactive dashboard that can easily
be extended for more complex visualizations.

## Web technologies, the what and the why

When I refer to web technologies, I refer to the components and protocols involved
in making web applications work, which includes:

- The languages used to write web pages, i.e. **HTML**, **CSS**, and **JavaScript**
- The web browser (or "client"), the application that runs on the user's machine and renders web pages
- The web server, a long running application, usually running on another machine, that communicates with
the client using the **HTTP** protocol. It accepts requests from clients, and sends responses back.
- Other protocols, such as **WebSockets** (which enables bi-directional, realtime communication between
clients and servers)

While the web browser can technically only render web pages written in HTML, CSS and JavaScript,
web servers do not have such limitations, and can be written in almost every language. In Python,
we write web servers using frameworks, such as **FastAPI**, **Flask**, **Quart** or **Litestar**. 
All that matters is that the application accepts HTTP requests, and returns responses that a
web browser would understand.

A simplified version of the interaction between browser and web server is shown in
the diagram below. 

![](/assets/interactive-apps/web-loop.svg)

As Python developers, we may want to minimize the amount of code we write in other
languages (e.g. HTML, CSS, JavaScript). While we can largely minimize the amount
of JavaScript we write, using tools like **htmx** (more on that later), HTML and CSS
remain necessary for us to layout web pages (although **Tailwind** can help us co-locate
the CSS with the HTML).



<!-- 

Web technologies, the what and the why

What do I mean by the term. Why are they a compelling tool in your toolbelt. Interactivity and allowing multiple clients, due to the idea of process decoupling (generic server; multiple clients)

Leveraging web technologies doesn’t necessarily mean we need to host our server. Instead, we can make the server a local only thing, meant to serve clients that will only run on our machines (multiple chrome tabs = multiple clients)

Our application

Dashboard with tables and charts, with dynamic data uploads with filters and static export 

Minimal library of see to update the dashboard when changes occur.

Illustration of the main loop
Launch the app, this will create the first version of each element of the dashboard, make the dashboard in HTML, and when we access the URL, we will see that html. 

When we update the value of a control, the client will tell the server to update the application state, which will then trigger a refresh of the dashboard

 -->





<!-- Thesis

Show off what can be done, example application.

Multi step processes, long-running, need for introspection and decision in
the middle -> need for interaction.

Interactivity - How it comes about and how it is enabled

    Halting and polling user
    Long running process that accepts user inputs
    

-->

Most Python applications are not interactive. They take a set of inputs, either
from a set of files or via command line arguments, perform an operation and have
a [side effect](https://en.wikipedia.org/wiki/Side_effect_(computer_science)) (e.g.
writing the output to a file or passing it to a service/API).

However, there are many situations where bringing in interactive would greatly
improve the user experience. One such situation is where your code is running
a multi-step process, where users would benefit from being alerted of step failures,
being allowed to manually fix some inputs, and carry on with the process. Another
example would be for tools whose purpose is to enable user analysis, like dashboards
or table viewers.

In this post, we'll go over the different ways Python scripts can be interactive,
and I'll show an example on how web technologies can be a powerful way to let your
users interface with your Python tools.

## Our project

To illustrate an interactive Python project, we will be building a dashboard
we can display in a web browser that will allow us to explore some data, take
notes, and export a static version of the dashboard for future reference (audit trail).

In terms of features, this tool will take the form of a library that allows
users to:

- write their own data loaders in Python (using `polars`);
- define tables and charts that depend on some state object;
- define how the state can be modified by the user of the dashboard, through controls; and
- define the layout of the dashboard and controls on the web page.

The rendering engine will be built in Python, but we will make a small use of a
mix of web technologies for the layout of our pages, to obtain lovely interactive
charts, and to enable the communication between the dashboard and the Python
engine.

## A useful framing of applications

If you've ever only built scripts in Python, you may be unfamiliar with the
"**client/server model**". The **server** is a long-running process that runs on
a machine you, the developer, control, which accepts connections from multiple
**client** applications, which run on your users' machines. 

Under this model, a Python script like the one below can be seen as a "client only" 
application. When the user calls it, the script will run in its own process,
which will die once the execution has finished.

```py
import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, default="Stranger")
    args = parser.parse_args(argv)

    print(f"Hello {args.name}!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

But most applications are actually made up of two sub-applications, one for clients
and one for the server, that can communicate with each other using some kind of
protocol (more on that later). 

![](/assets/interactive-apps/server_client.svg)

## Web technologies

On the web, we have the luxury of having extremely powerful clients, in the form
of **web browsers**. Because these applications target web browsers, they need to
use **HTML** ("Hypertext Markup Language") for the markup of the page, **CSS** ("Cascading Style Sheets")
for styling, and **JavaScript** for interactivity.

On the server side, anything goes! As long as the language allows us to build
a long-running process that can listen for HTTP ("Hypertext Transfer Protocol") requests,
it can be used to build a web application's back-end (i.e. the server).

For example, Python has an `http` package as part of its standard library, which
allows us to write a basic HTTP server like such:

```python
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer


# This handler's methods get called when the server receives a request from
# a client. In this example, we only implement a handler for GET requests.
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"Hello, World!"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    # The server will run on localhost (i.e. our machine), on port 1234
    server_address = ("localhost", 1234)
    httpd = HTTPServer(server_address, Handler)

    # This is our infinite loop, where the server listens for incoming
    # requests
    httpd.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
```

Of course, no one builds HTTP servers this way. Instead, we leverage on 
frameworks like [Flask] and [FastAPI] so we can be more efficient with our typing.  

As shown below, we can use template strings to allow parameters in the URLs we
will be making requests to, and we can define different kinds of response types (including HTML).

```python
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/{id}/plain")
def plain(id: str):
    return f"Hello {id}!"


@app.get("/{id}/json")
def json(id: str):
    return JSONResponse({"message": f"Hello {id}!"})


@app.get("/{id}/html")
def html(id: str):
    return HTMLResponse(f"<h1>Hello {id}!</h1>")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=1234)

```

After running this script, you can visit 

![](/assets/interactive-apps/simple-html.png)





---




If you're reading this, I'm sure you're comfortable with Python and you've built
your fair share of scripts and Jupyter notebooks in your days. But you may also
feel a certain itch, the one that makes you want to build things that user can
touch and feel. A tool that is more than transforming data, something visual,
something... more.

In this blog post, I will discuss how web technologies are a great way for you
to build user interfaces for your Python applications, whether or not you intend
to use the web to distribute said applications. 

If that sounds good, read on!


<say we're going to build an application>

## Our application

We will build an interactive dashboard used for the monitoring of some key
metrics of an investment portfolio, which will also allow us to jot some notes
down, which will be saved to disk. Finally, the application will allow us to
generate a static version of the dashboard (including the notes), which will
serve as audit trail.

Here are the high level features we will require:

- 





Most people I know building with Python today are building things that fit within of three categories:

- Jupyter notebooks for one-off data analysis tasks;
- Non-interactive scripts with arguments provided via the command line; or
- Web applications using frameworks like Django/Flask/FastAPI.

Automation work usually takes the form of scripts, since Jupyter notebooks are a notoriously poor experience for that use case, 
and full-fledged web applications may seem overkill for the job.

However, the lack of interactivity provided by scripts (unless you go with a framework like `textual`) makes them 
hard to use when one part of your workflow involves exploratory analyses. They can also become quite difficult to use
for people who are not comfortable around a terminal (which is a non-negligible piece of the Python developer population). 

How do we go from building scripts to building applications using Python? In this post, I talk about a mix between Python
and web technologies can enable you to build better user experiences. [TBD]

## User interfaces

Users want to interface with our applications. They want to tell it what to do, 
configure it, analyse results, etc. Your options for building these interfaces are:


......


Thesis: Soup up your Python applications with web interfaces.
Interactive applications using Python and web technologies

How do you build interaces in Python?

- Terminal UI -> Textual
- Tkinter/PyQt -> Native applications
- ... Web interfaces

Web interfaces are generally more convenient, because web applications are ubiquitous,
and resources and tools are plentiful.






## Servers and clients




The user calls the script via their terminal, the script runs, and the Python
process ends. If another user calls that same script, it will run again from
scratch. In other words, there exists no common state.






However, scripts can be limiting in where they can be run, since they require direct access to the script files
or a Python environment with those scripts installed (e.g. as `uv` tools). This can quickly become a distribution
nightmare for bigger teams, since now you have to think about where those packages will be hosted, how they can
be pulled on users' machines, versioning, etc.







Most Python tools out there are "data processors". They read data from files and user inputs, perform calculations and spit out data or charts.

![](</assets/building-scrappy-apps/illustration.svg>)

Some developers may feel a little adventurous and build a Graphical User Interface ("GUI") to help their users run their tasks, using libraries like `tkinter` or `PyQt5`, but those can be notoriously difficult to package and share around. 

...

In this post, I will go over how well-known Python packages and web technologies can be used to build a highly interactive portfolio monitoring tool that requires no special infrastructure, only a modern browser on a laptop.

## Web technologies

When I refer to "web technologies", I am talking about the set of languages, protocols and tools used to build web applications (think Gmail, Netflix, or even LinkedIn). This includes technologies such as:

- **HTML** ("Hypertext Markup Language"), the language that defines the structure of web pages;
- **CSS** ("Cascading Style Sheets"), the language that defines the styling of these pages;
- **JavaScript**, the programming language your web browser can understand and execute;
- **HTTP** ("Hypertext Transfer Protocol"), the main protocol used to access web resources;
- **WebSockets**, a protocol used for bidirectional communications between your web browser and web servers.

But those are not Python. So why would we bother bringing in all this additional complexity into our applications?

The reason is quite simple: **The web browser is a great way of building and running interfaces**.

Think about it. Ever wondered why your favorite web application looks and behaves the same regardless of where you're accessing it (even on mobile)? 

And with libraries like `htmx`, you don't even have to know Javascript.

Different kind of applications:

- Deployed on Internet (requires infrastructure and thinking about security)
- Deployed on local network only accessible by your company (requires infrastructure to have the app available 24/7, it has to be deployed on a server)
- Not deployed at all (the app lives on your machine, but uses the browser as an interface)


The first kind is out of the question. The second one can be considered, but requires your organization to have systems in place to deploy business apps. Understandably, it is often complicated because IT will need to make sure the developers cannot mess up the server in any way.

The third kind however can be interesting, and we can enable some form of consistency across users by using network files for example.


## Our application

Our application will be a monitoring tool that will enable a small team to assess some Key Performance Indicators ("KPI") of a financial portfolio, and analyze them visually. They will launch the application on their machine, which will pop a webpage 

