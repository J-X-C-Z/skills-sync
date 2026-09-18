---
name: orchestrate-multi-agent-project
description: "Orchestrate persistent multi-agent project development with explicit role awareness: one project steward conversation, reusable leader conversations inside the same project for stable work domains, and short-lived subagents for concrete execution. Enforce who may create which kind of conversation, especially preventing Leaders from opening new sessions. Use whenever a project needs roadmap delegation, same-project leader creation or reuse, cross-leader dependency management, batched progress reporting, delegated review, or control of multi-agent task granularity."
---

# Multi-Agent Project Orchestration

Coordinate long-running projects through three levels. The Steward and every Leader conversation belong to the same project; the project is the boundary for shared context, roadmap ownership, and coordination.

1. **Project Steward** — one persistent project-level conversation.
2. **Leader** — persistent conversations responsible for stable work domains or roadmap areas.
3. **Subagent** — short-lived execution workers created inside a Steward or Leader conversation.

Keep long-term context in persistent conversations and use Subagents for concrete, verifiable execution. This reduces cross-conversation overhead while keeping the Project Steward responsive.

## Core model

```text
Project
└── Project Steward
    ├── Steward Subagents
    ├── Leader A
    │   ├── Subagent A1
    │   └── Subagent A2
    ├── Leader B
    │   ├── Subagent B1
    │   └── Subagent B2
    └── Leader C
```

Do not turn every task into a new conversation. Prefer stable Leader conversations plus temporary Subagents.

## Role awareness and session guard

At the beginning of every turn, identify the agent's role, project, parent conversation, current Roadmap Package, and permitted child type before delegating work or creating anything. Use this compact identity:

```text
Role: Project Steward | Leader | Subagent
Project: <current project>
Parent: <parent conversation or none>
Current Package/Task: <one line>
Permitted Child: Leader conversation in this project and/or Subagent in this conversation | None
```

The role determines authority; the task's size or urgency never grants additional authority. If role or project cannot be established, pause creation and report the missing context to the parent.

| Role | May create | Must not create |
|---|---|---|
| Project Steward | A justified Leader conversation inside the current project; Subagents inside the Steward conversation | A Leader in another project or as projectless |
| Leader | Subagents inside the current Leader conversation | Any new persistent conversation, session, fork, or another Leader |
| Subagent | Nothing persistent; complete its assigned task | Any session, management layer, roadmap, or direct Steward channel |

The Steward has two separate child capabilities: it may create a justified Leader conversation inside the current project, and it may create review, audit, investigation, or integration Subagents inside the current Steward conversation. Steward Subagents are execution workers, not new Leaders, and do not create another persistent management layer.

After the Steward assigns a Roadmap Package, the Leader continues in its existing Leader conversation and decomposes the package into Subagents there. A Leader must never interpret “split the work,” “delegate,” or “run in parallel” as permission to open a new session. If a creation tool offers a new conversation, fork, or projectless target, it is unavailable to the Leader for this purpose.

## Authority boundaries

The Project Steward may:

- maintain and modify the project roadmap;
- assign roadmap packages to Leaders;
- communicate with every Leader;
- create a new Leader conversation inside the same project when justified;
- create Subagents inside its own conversation;
- delegate reviews, audits, integration checks, or investigations to its own Subagents;
- accept, reject, or return Leader results;
- resolve cross-domain architectural decisions.

The Project Steward may create Subagents in its own conversation at any time that independent execution or review helps preserve responsiveness. These Subagents report back to the Steward and do not become Leaders.

A Leader may:

- manage its assigned work domain;
- decompose its current roadmap package;
- create Subagents inside its own conversation;
- coordinate its Subagents;
- communicate directly with other Leaders about dependencies and interfaces;
- integrate and validate work before reporting upward.

A Leader must not create another Leader conversation or any new session. If a new persistent work domain is needed, report the recommendation to the Project Steward. The Steward must create the new Leader using the current project's context; never create it as a projectless conversation or attach it to another project. If the Steward's project context is unavailable, resolve that before creating the Leader or report the blocker.

A Subagent remains subordinate to the conversation that created it. It should complete one clear task, produce one clear output, and meet one clear acceptance standard. It must not manage the project roadmap, create a persistent management layer, bypass its parent, or report routine details directly to the Steward.

## Reuse Leaders before creating new ones

When new work appears, evaluate it in this order:

1. Determine whether an existing Leader owns the relevant domain.
2. If so, continue in that Leader conversation.
3. If the work is temporary or narrow, assign it to the closest existing Leader and let that Leader create Subagents.
4. Create a new Leader inside the current project only when the work is a durable, distinct domain that benefits from independent persistent context.

Do not create a Leader merely for one feature, page, bug, pull request, experiment, or isolated implementation task. Strong evidence for a new Leader includes a continuing roadmap, recurring work, substantial independent context, stable boundaries with other domains, or significant context pollution if placed under an existing Leader. When uncertain, reuse an existing Leader.

## Delegate roadmaps, not microtasks

The Project Steward assigns one coherent **Roadmap Package** to each Leader by default, rather than a sequence of implementation instructions. Define:

- objective;
- scope and out-of-scope boundaries;
- deliverables;
- acceptance criteria;
- constraints;
- dependencies;
- affected shared interfaces;
- reporting trigger.

After delegation, let the Leader decide how to decompose and execute the package. Read `references/templates.md` when constructing a Roadmap Package.

## Leader execution

After receiving a Roadmap Package, the Leader should:

1. understand the objective and boundaries;
2. inspect relevant existing project state;
3. split the roadmap into concrete execution tasks;
4. identify tasks that can run in parallel;
5. create Subagents for suitable tasks inside the current Leader conversation;
6. coordinate dependencies between them;
7. integrate their work;
8. validate the integrated result;
9. batch meaningful progress before reporting to the Steward.

Do not report each completed microtask separately. Complete a meaningful integrated batch whenever practical.

## Communication granularity

Allow fine-grained communication between a Subagent and its parent conversation: implementation results, test failures, discovered bugs, missing dependencies, clarification requests, and local design choices.

Use coarse-grained, high-information communication between a Leader and the Project Steward. Report milestones, integrated deliverables, blockers, architectural decisions, scope changes, breaking interface changes, cross-team conflicts, and serious security, correctness, or data risks. Do not report routine file edits, ordinary test progress, or local implementation details.

Leaders may communicate directly when work crosses domain boundaries. Keep that communication centered on interfaces, API contracts, schemas, dependencies, shared resources, integration order, breaking changes, and ownership boundaries. Do not use cross-Leader communication for ordinary internal implementation details. Read `references/coordination-protocol.md` for escalation and cross-Leader coordination.

## Escalate immediately when necessary

A Leader must report without waiting for the normal batch boundary when it encounters:

- a blocker preventing meaningful continuation;
- a required change to core architecture;
- a material scope expansion;
- a breaking public interface or schema change;
- an unresolved cross-Leader conflict;
- a security risk;
- potential data loss or corruption;
- a decision outside the Leader's authority.

Otherwise, continue working and report in batches.

## Keep the Project Steward responsive

When a Leader submits substantial work:

1. acknowledge and classify the report;
2. create Steward-side review Subagents when independent verification is useful;
3. let them inspect implementation, tests, architecture, security, or roadmap compliance;
4. continue processing other Leader reports and project-level decisions;
5. act on the review result when it returns.

The review Subagent advises. The Project Steward makes the final project-level decision. Do not make the Steward a serial review bottleneck.

## Maintain project state

Maintain a compact Project Registry containing the current roadmap, existing Leaders and ownership, each Leader's active Roadmap Package, major cross-Leader dependencies, pending decisions, pending reviews, accepted milestones, and known risks. Update it after material changes. Detailed task state belongs inside the relevant Leader conversation; the registry is not a microtask tracker.

## Completion behavior

When a Leader finishes its current Roadmap Package:

1. integrate relevant Subagent results;
2. perform available validation;
3. submit one consolidated Leader Report;
4. wait for acceptance, requested changes, or the next Roadmap Package.

Do not autonomously expand into a new major roadmap area without Steward approval. After accepting work, the Steward updates project state, resolves resulting cross-domain changes, confirms ownership, and assigns the next package when appropriate.

## Reference loading

Read `references/coordination-protocol.md` when deciding whether to create a same-project Leader, coordinating multiple Leaders, handling blockers or ownership conflicts, deciding reporting granularity, or delegating review.

Read `references/templates.md` when assigning a Roadmap Package, writing a Leader Report, requesting work from another Leader, recommending a new Leader, or reporting a review result.
