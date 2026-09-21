---
title: Keeping Myself in the Loop for Agentic Software Work
posted_on: 2026-07-13
last_update: 2026-07-13
draft: false
abstract: >
    A lightweight private workflow for reviewing agent-generated HTML artifacts
    from a phone, using Tailscale, a file server, and a small gallery application.
---

Selecting what work is worth doing has always been an art. We are finite
beings, and our time needs to be spent wisely if we do not want to look back
with regret. In the age of agents, that picture has changed: experimenting has
become cheaper, at least in terms of time. As such, more of our attention can
go towards identifying the right problems, deciding what good looks like, and
doing the engineering work that benefits most from human judgment.

The power of agents means that some people have become happy to outsource much 
of their thinking to them. Others prefer setting more granular decision boundaries
in order to keep a better mental model of the codebase and avoid future headaches.

I am firmly in the latter camp. But that means I have to accept I am the bottleneck
in a larger system, and I now have to be smart in managing how this affects the
whole system's output velocity. 

In this post, I will show a very simple concept applied to enable my review 
workflow for agent-generated code, and the subsequent decision-making process: 
browsable review artifacts I can access and manage via my phone.

## The asynchronous review problem

If you have worked in teams (especially remote ones), you know that
asynchronous collaboration is the name of the game. To review someone's work
without relying on them being available at the same time, you need a useful set
of artifacts to inspect after the work has been delivered.

When working with agents, much more of the review work may be done away from your
desk, given the "continuous" nature of these agents, and the sheer volume they
generate. It does however require you to choose your own acceptable review surface.

Should you review all the code? Can you even build a good enough mental model just
by reading the code? Imagine your agent has cranked out a fully-fledged 
financial model. You can understand the components of the model by reading the
code, but you will most likely not be able to fit the whole model in your head
when assessing it. 

Fortunately, agents are quite good at creating interactive HTML visualizations
with embedded data. In our example, we can ask that the agent generates a script
that will run a model and save every outputs (even intermediate ones), and
stick it into an interactive visualization. 

But how can we make sure we can even access the generated file on our phone? 

## Access your agent's machine outside its network

Whether your agent is running on a VPS on your local machine, your agent's 
companion application (e.g. ChatGPT or Claude) allows you to access your sessions
remotely, without the need to be on the same network. This is what has enabled 
so many people to work with agents away from their keyboard.

But not every piece of functionality can be provided in an optimal way via said
application. For example, integrating HTML visualization in my review workflow
requires it to be clickable inside a Github pull request. I also need to be able
to mark which artifacts I have already reviewed, which is a deterministic action
I shouldn't need an agent doing on my behalf.

As such, I settled on a custom application with a web frontend that will show
me the artifacts in my review queue and allow me to "mark" them as reviewed,
from my phone, but not deployed to the open Internet.

As first described in [another post](/posts/simple-deployment-for-personal-apps), 
Tailscale is the perfect fit for this kind of private internal applications. As
long as you have an application running on `127.0.0.1:<port>` on your local machine,
you can use `tailscale serve` to serve it to your tailnet (i.e. the mesh network
created from your devices connected to the machine).

The simplest example is a barebones Python file server, which can be launched
and served like so:

```bash
python -m http.server --directory path/to/dir 9797
# Serving HTTP on :: port 9797 (http://[::]:9797/) ..

tailscale serve --https 9797 9797
# Available within your tailnet:

# https://mmbp.follow-scylla.ts.net:9797/
# |-- proxy http://127.0.0.1:9797

# Press Ctrl+C to exit.
```

Now, when we navigate to tailnet's URL on the phone, we see the following. (Clicking
on the links will show the files' contents)

```raw_html
<center>
<img
  src="/assets/keeping-myself-in-the-loop-for-agentic-software-work/file-server-tailscale.png"
  alt="Tailscale serving the local file server"
  style="width: 60%;"
>
</center>
```

This is enough to reach an artifact, but it is not a workflow enabler just yet.
A directory listing does not show which artifacts need my attention first or
whether I have already reviewed them. That is the gap I wanted to fill with a
dedicated gallery application.

## The setup

I run two small servers on my machine:

- One that serves the files themselves, on port `8766`;
- Another that serves the gallery application, on port `8765`.

Both watch `~/review-artifacts`. I keep them separate because the artifacts are
untrusted HTML, while the gallery needs filesystem access. In practice, marking
an artifact as reviewed moves its directory into `.reviewed`, which the gallery
displays differently.

```raw_html
<center>
<img
  src="/assets/keeping-myself-in-the-loop-for-agentic-software-work/gallery-application.png"
  alt="The gallery application"
  style="width: 60%;"
>
</center>
```

The important part is a short convention in my global `AGENTS.md` file, which
means I do not have to repeat the request in every prompt:

```markdown
...

## Review artifacts

Create a mobile-friendly Review Artifact at
`~/dev/review-artifacts/<project>-<slug>/index.html`. Keep its supporting
files in the same directory, verify it at a phone-sized viewport, and return
its direct Tailnet URL after publishing.

When a pull request includes a Review Artifact, include that URL under a
`## Review artifact` heading and verify that it resolves before opening the
pull request.
```

## The workflow by example

Say I have access to a `prices.parquet` file with three years of close-price
data for stocks and ETFs. I ask an agent to calculate daily returns, then
produce three rolling risk measures:

- annualised 20-day sample (ex-ante) volatility;
- a 20-day GARCH volatility forecast; and
- a 99% one-day historical-simulation Value at Risk using two years of
  observations.

The agent writes the functions, runs them against the supplied data, saves the
output to another `.parquet` file, and produces an artifact. The prompt is
deliberately concise:

```markdown
Calculate daily returns, 20-day sample and GARCH volatility, and 99% historical
one-day VaR from `timeseries.parquet`. Then publish an HTML review artifact that
charts the measures by ticker, prioritising securities with the largest one-day
returns so I can inspect each measure's response.
```

The agent returns a direct link to the artifact, and the gallery shows it in my
review queue, where I can mark it as reviewed.

```raw_html

<div class="flex gap-8 w-full items-center justify-center">
<img
  src="/assets/keeping-myself-in-the-loop-for-agentic-software-work/gallery-with-risk-measure.png"
  alt="The gallery including the produced artifact"
  style="width: 50%;"
>
<img
  src="/assets/keeping-myself-in-the-loop-for-agentic-software-work/example-artifact.png"
  alt="The produced artifact"
  style="width: 50%;"
>
</div>

```

In a GitHub-based workflow, the pull request carries the same link:

```markdown
...

## Review artifact

[https://mmbp.follow-scylla.ts.net:8766/example-workflow-risk-measures/index.html](https://mmbp.follow-scylla.ts.net:8766/example-workflow-risk-measures/index.html)

```

This is a much better unit of review for a phone. I do not need to establish
that every line of the implementation is correct there. Instead, the artifact
helps me decide where a deeper code or domain review is warranted.

In this case, the artifact also highlighted a data issue: one stock showed an
extreme one-day return that could not be reconciled with a third-party dataset.

The first artifact will not always be satisfactory. When it is not, I can point
out problems such as a confusing layout or poor responsiveness from my phone,
then check the next version as the agent updates it.

## Conclusion

This is a small experiment, not a claim that a phone can replace proper code
review, tests, or domain expertise. It can, however, give me a better decision
point while an agent is doing more of the mechanical work: instead of simply
reporting that a task is complete, the agent gives me a self-contained output I
can inspect and challenge.

Tailscale and the gallery are only the plumbing. The important convention is
that a review artifact is published to a predictable place, works on a small
screen, and is linked from the session or pull request that it supports. That
makes the output reviewable when I have a few minutes away from my desk, rather
than only when I am back at it.

I am not trying to remove myself from the loop. I am trying to make that loop
more concrete and less of a bottleneck. As agents make experimentation cheaper,
I want to spend more time deciding what is worth building, challenging what has
been produced, and refining the work that holds up.
