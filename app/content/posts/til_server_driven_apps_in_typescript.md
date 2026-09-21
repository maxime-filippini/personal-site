---
title: TIL - Server-driven applications using Typescript
posted_on: 2025-09-15
last_update: 2025-09-15
draft: true
abstract: >
    TBD
---

<!-- 

"Hey, here's something interesting".

Big picture, how to build web apps, no need for an in depth explanation of everything.

Maybe a little explainer about the pieces that make up a web application.
    Application server, serving requests.
    Database.
    Maybe some sort of external queue for background jobs.
    Auth as a component.

What does the server respond with? Data or HTML. MPA is fully HTML, SPA is fully data.

Focus on ergonomics of JSX, use of server-side TS libraries for good DX (drizzle + betterauth)

-->


Developing for the web is appealing, as the technological marvels that are web-browsers allow for effective cross-platform distribution of your applications, but it comes with its lot of complications. Front-end frameworks, build tools, handling the link between client and servers via an API, authentication, databases, etc. That's quite a lot to have set up to get started.

What if we could build applications without needing to worry about client state, and no complex build step? Here's a very productive stack that you might enjoy!


## The stack

The basic idea behind the stack is for it to be **server-driven**, which will bring productivity by removing front-end complexity. 



## High level stack overview

For building a web application, we need a "web server", i.e. a long-running process that listens for HTTP requests from clients and responds to these client with, you guessed it, HTTP responses.

Because we want to be super productive, we'll use [ElysiaJS](https://elysiajs.com/), a Typescript server that runs on the [Bun](https://bun.sh/) runtime, as it provides excellent type inference, and has a very tight syntax. See the example below for a "Hello, World!" kind of server.

```ts
import { Elysia } from 'elysia'

new Elysia()
    .get('/', 'Hello Elysia')
    .get('/user/:id', ({ params: { id }}) => id)
    .post('/form', ({ body }) => body)
    .listen(3000)
```

On the frontend, we'll be using [htmx](https://htmx.org/), a great Javascript library that will allow us to have a snappy experience in the browser, while keeping our application server-driven. The only requirement htmx imposes on us is that our web server needs to return HTML on certain routes, so that it can take that HTML and put it where we need it on the page.

For our server to return HTML dynamically, we need some kind of a **templating library**. In Javascript, there are a lot of choices, such as:

- [Handlebars.js](https://handlebarsjs.com/)
- [Mustache.js](https://github.com/janl/mustache.js)
- [Pug](https://pugjs.org/)
- [Nunjucks](https://mozilla.github.io/nunjucks/)

**But we're not going to use any of those!** Instead, we will go with the solution I find to be the most elegant: [JSX](https://en.wikipedia.org/wiki/JSX_\(JavaScript\)).

JSX is mostly known for its use within the React framework, which means its most common use case is for it to be running **on the front-end**, i.e. building HTML at runtime using Javascript that runs in your web browser. But JSX is just a syntax, and can theoretically be used in other runtime (and it actually does, e.g. [React Server Components](https://react.dev/reference/rsc/server-components)).

Because we will be using htmx and not React, we need to use an HTML engine that supports JSX without needing to bring in the entire React machinery. This functionality is provided by the [`@kitajs/html`](https://kitajs.org/html/) package.




...





The premise of this post is simple, show you what I would consider a productive setup for building web applications.


## Components of a web application

Most web application has at the very least two components:

- A "front-end", i.e. code that runs in the browser to display your application to your users;
- A "back-end", i.e. a server whose primary role is to provide the resources for the front-end to do its job (data).

The level of sophistication of the front-end and back-end of an application depends on what it tries to do. For example, the role of the back-end serving a simple static page will only be to serve "static assets", like HTML files and images. But for a highly complex social network? The back-end server will be in charge of authentication, building the connection graphs, run machine learning models, pushing notifications, in addition to serving user requests. Same thing goes for the front-end, where a single Javascript file may be sufficient for a small static website, but for bigger applications the front-end starts blending with the back-end thanks to Server-Side Rendering ("SSR"), with client code that requires complex build steps to be able to be served by the browser, etc.

While large organizations have dedicated front-end and back-end teams, startup and solo developers need to be able to build for both sides, requiring a "**full-stack**" experience.

Historically, building a full-stack application as a solo developer would most often require you to build a "Single Page Application" (or "SPA") using a Javascript framework like [React](https://react.dev/), [Svelte](https://svelte.dev/), or [Vue](https://vuejs.org/), and have your back-end provide an API that the SPA will use to get data from your server. 

While this approach is still viable, front-end "metaframeworks" that allow you to write React (via [NextJS](https://nextjs.org/)), Svelte (via [SvelteKit](https://svelte.dev/docs/kit/introduction)), or Vue (via [Nuxt](https://nuxt.com/)) on the server have become part of the zeitgeist, boasting great Developer Experience ("DX") by blurring the line between client code and server code, using the same language on both sides (Javascript or Typescript).

But this amalgamation of client and server code is not without complexity, as developers become confused about where code runs, which can lead to glaring security issues (e.g. checking authentication state client-side).

On the other hand, tools like [htmx](https://htmx.org/) allow the back-end to drive front-end experiences, which limits complexity as dedicated front-end code becomes unnecessary.

## What htmx does and needs

htmx's core idea is simple. Have your back-end return HTML, and it will take care of putting it where you need it on the page.

That's it. htmx doesn't require anything else from you. That means you can use [whatever back-end technology you like](https://htmx.org/essays/hypermedia-on-whatever-youd-like/). Yes, even a Javascript/Typescript based framework!

```note
Most people may scowl when thinking of pairing htmx and Javascript, as the former is often viewed as a way to not have to learn the latter. The argument here is that, even if you use a Javascript server (running on NodeJS, Deno, Bun or any other runtime), using htmx will free you of having to deal with **client-side complexity**, while still benefiting from the great DX brought forth by the Javascript ecosystem.

More on that later.
```

Here are some options you may want to consider depending on your language:

| Language   | Web frameworks                                                                                |
| ---------- | --------------------------------------------------------------------------------------------- |
| Python     | Flask, FastAPI, LiteStar, Django Ninja, Django                                                |
| Go         | Gin, Fiber, Echo, Chi                                                                         |
| Javascript | Express, Fastify, Hono, Elysia, Deno (provided by the runtime), Bun (provided by the runtime) |
| Gleam      | Wisp, Mist                                                                                    |
| Elixir     | Phoenix, Sugar                                                                                |

Because our back-end needs to respond with HTML, we need a good way to write said HTML in our language of choice. The common way to do so is to use a templating engine. In Python, this will usually be [jinja2](https://jinja.palletsprojects.com/en/stable/) or [Django templates](https://docs.djangoproject.com/en/5.2/topics/templates/), but I'm not a big fan of those because they're basically a full-fledged language that you need to learn and whose limitations you need to deal with.

Personally, I prefer approaches that are more integrated in the language. In Python, you can use `htpy`, an HTML builder library that lets you take advantage of Python language features like functions and lists. In Javascript, it turns out we can use [JSX](https://en.wikipedia.org/wiki/JSX_(JavaScript)) inside our files, which is as close as HTML as it gets, with some nice extra features!

## Using JSX on the server

JSX is mostly known for its use within the React framework, which means its most common use case is for it to be running **on the front-end**, i.e. building HTML at runtime using Javascript that runs in your web browser. But JSX is just a syntax, and can theoretically be used in other runtime (and it actually does, e.g. [React Server Components](https://react.dev/reference/rsc/server-components)).

Because I will be using htmx and not React, I need to use an HTML engine that supports JSX without needing to bring in the entire React machinery. This is what [`@kitajs/html`](https://kitajs.org/html/) provides.

Take the following example of a list of links:

```tsx
// example.tsx

const Example = ({ items }: { items: { label: string; href: string }[] }) => {
  return (
    <div>
      <ul>
        {items.map((item) => (
          <li>
            <a href={item.href}>{item.label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
};

console.log(
  <Example
    items={[
      { label: "Home", href: "/" },
      { label: "News", href: "/news" },
      { label: "About", href: "/about" },
    ]}
  />
);
```

Try to run this with a runtime that supports running `.tsx` files directly (e.g. Bun), and you get:

```html
<div>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/news">News</a></li>
        <li><a href="/about">About</a></li>
    </ul>
</div>
```

Pretty nifty! Our function looks super clean and does what it needs to.

Just like in React and other component-based frameworks that use JSX, we can compose our elements and layouts very easily. Consider the following layout:

```tsx
import { Children } from "@kitajs/html";

type LayoutProps = {
  children: Children;
  isLoggedIn: boolean;
};

export const Layout = ({ children, isLoggedIn }: LayoutProps) => {
  const loginStatus = () => {
    if (isLoggedIn) {
      return <p>You are logged in!</p>;
    }

    return <button>Log in</button>;
  };

  return (
    <html>
      <head>
        <title>My website!</title>
      </head>
      <body>
        <div>{loginStatus()}</div>
        <div>{children}</div>
      </body>
    </html>
  );
};
```

Composition is done using the XML-like syntax of JSX, i.e.

```tsx
console.log(
  <Layout isLoggedIn={false}>
    <Example
      items={[
        { label: "Home", href: "/" },
        { label: "News", href: "/news" },
        { label: "About", href: "/about" },
      ]}
    />
  </Layout>
);
```

```html
<html>
  <head>
    <title>My website!</title>
  </head>
  <body>
    <div>
      <button>Log in</button>
    </div>
    <div>
      <div>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/news">News</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </div>
    </div>
  </body>
</html>;
```

```note
For this set up to work, the following lines have to be included in the `tsconfig.json` file associated with the project. This is what will tell the runtime to use `kitajs` as the HTML renderer.

`"jsx": "react-jsx",`

`"jsxImportSource": "@kitajs/html",`

`"plugins": [{ "name": "@kitajs/ts-html-plugin" }],`
```

## Actually running a server with ElysiaJS

For us to be able to leverage JSX as an HTML templating language, we need to bring in a Javascript or Typescript server. These days, we have a lot of options available, but I will be using [ElysiaJS](https://elysiajs.com/), which prides itself on its ergonomics and performance (thanks to the Bun runtime).

Let's start with a Hello World app and see what it looks like in Elysia with JSX:

```tsx
import html from "@elysiajs/html";
import Elysia from "elysia";

const app = new Elysia()
  .use(html())
  .get("/", () => {
    return (
      <div>
        <p>Hello, World!</p>
      </div>
    );
  })
  .listen(3000);

console.log(
  `🦊 Elysia is running at http://${app.server?.hostname}:${app.server?.port}`
);

```

![](/assets/elysia-jsx-hello-world.png)

Here, we use the `html` plugin from Elysia, allowing us to return HTML from our routes, which is a must-have when using htmx. Then, when a user visits the root of our website, we gree them with the _"Hello, World!"_ message.

Simple enough.

<!--  More stuff about Elysia JS -->


## Let's implement an htmx example

To show the ergonomics of writing an application with ElysiaJS and htmx, let's
write the form-editing example [provided by htmx](https://htmx.org/examples/click-to-edit/).

