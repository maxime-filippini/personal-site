---
title: How I would build a Python platform for small teams
posted_on: 2025-10-30
last_update: 2025-10-30
draft: true
abstract: >
    TBD
---

**Imagine you are tasked with uniformizing Python development practices between a few small teams**. Currently, these teams are building small scripts and running them on their machine, which poses concrete issues of productivity, since the wheel ends up being re-invented, and security, since no centralized controls over third party dependencies exist.

In this post, I'll go over how I would go and build a platform to empower these teams to do their best work. In my opinion, here are the requirements of such a platform:

- It needs to be integrated with a source code management platform that supports automation;
- A repository of pre-approved third party packages;



## Version control

No development work should be performed outside of a **version control system** (or "VCS"). Teams will have to be using Git locally in order to track their changes. This will most likely require some training, but it cannot be avoided.

When changes are committed locally, they should be pushed to a **remote repository** that will constitute the **source of truth** every developer will be able to trust and use.

For this, we basically have two choices:

- Self-host a server, using an open source solution like Gitea; or
- Use a hosted service, like GitHub.

For small teams, I would recommend the latter.

## Workflows
