# Coordination Protocol

Use this reference for hierarchy decisions, communication, escalation, and review.

## 1. Persistent context model

The hierarchy separates context ownership from execution capacity:

```text
Persistent context:
Project Steward
Leader
Leader
Leader

Temporary execution:
Subagent
Subagent
Subagent
```

A persistent conversation should exist because its context will continue to be useful. A Subagent should exist because a concrete unit of work needs execution. Do not promote temporary work into a persistent conversation without a durable reason.

## 2. Role bootstrap and creation guard

Every agent should begin by declaring or confirming:

```text
Role:
Project:
Parent conversation:
Current package or task:
Permitted child:
```

Use the following authority matrix:

| Role | Creation authority | Boundary |
|---|---|---|
| Project Steward | May create a justified Leader conversation in the same project, or a Subagent in the Steward conversation | Must preserve the current project context |
| Leader | May create Subagents in the current Leader conversation | May not create a new conversation, session, fork, or management layer |
| Subagent | No persistent creation authority | Reports to its parent only |

The Steward has both kinds of child authority shown above: it can create a same-project Leader conversation, and it can create Subagents inside the current Steward conversation for review, audit, investigation, or integration. These are different operations; a Steward Subagent does not become a Leader.

The Leader's work begins after receiving a Roadmap Package by inspecting and using its existing conversation. “Create Subagents” means in-conversation workers under that Leader; it does not mean opening new sessions. If the Leader has no way to create an in-conversation Subagent, report that capability gap to the Steward rather than opening a new session as a substitute.

If a Leader accidentally opens a new session, stop treating that session as part of the hierarchy, report the violation to the Steward, and return the work to the original Leader conversation. Do not continue building a second management layer.

## 3. Operating level by role

The Project Steward owns project-level coherence. Maintain awareness of the project purpose, roadmap, architecture, major decisions, Leader ownership, inter-domain dependencies, integration state, pending reviews, and major risks. Operate primarily at:

```text
Project → Roadmap → Work Domain → Milestone
```

Operate at function, file, or line level only when investigating a problem or auditing a result.

A Leader owns one durable work domain and understands it more deeply than the Steward needs to. Maintain locally the internal task breakdown, implementation context, local technical decisions, active Subagents, unfinished tasks, and domain-specific tests and issues. Promote information upward only when it affects project-level coordination.

## 4. Leader creation decision

All Leader conversations created by the Project Steward must be inside the same project as the Steward. Preserve the current project's identity and context when creating the conversation. Never create a projectless Leader or attach it to another project. If the Steward's project context cannot be determined, stop the creation decision and resolve that context first.

Use this decision tree:

```text
Does an existing Leader reasonably own this work?
│
├── Yes → Reuse that Leader.
│
└── No
    │
    ├── Is this temporary or narrowly scoped?
    │   ├── Yes → Assign to the closest Leader and use Subagents.
    │   └── No
    │
    └── Is this a durable independent work domain?
        ├── No → Reuse the existing structure.
        └── Yes → The Steward may create a Leader conversation inside the current project.
```

Strong evidence for a new Leader includes a separate technical domain, independent persistent context, repeated future tasks, an independent roadmap, substantial ongoing workload, and regular interfaces with other domains. Temporary work volume, one complex feature, one difficult bug, or a desire for additional parallelism are weak evidence. Parallelism alone does not justify a new Leader; use Subagents for parallelism.

## 5. One active Roadmap Package by default

Keep each Leader focused on one active Roadmap Package unless the Steward explicitly decides otherwise. A package may contain multiple tasks and many Subagents. “One package” means one coherent milestone or development stage, not one small task. This prevents fragmented context, partial completion across initiatives, excessive upward reporting, and unclear priorities.

## 6. Communication matrix

| Sender | Receiver | Default granularity | Purpose |
|---|---|---|---|
| Subagent | Leader | Fine | Execution details |
| Leader | Subagent | Fine | Concrete task delegation |
| Leader | Steward | Coarse | Milestones, decisions, blockers |
| Steward | Leader | Coarse | Roadmap packages, priorities |
| Leader | Leader | Medium | Interfaces and dependencies |
| Steward Subagent | Steward | Medium/Fine | Review evidence |

The higher communication crosses the hierarchy, the more compressed and decision-relevant it should become.

## 7. Batching rule

Report after a meaningful integrated batch. Good boundaries include an API layer implemented and tested, one end-to-end communication path working, one UI module integrated with data, one migration stage completed, a related group of defects fixed and regression-tested, or a design-system foundation completed.

Avoid messages such as “created one file,” “starting the next task,” or “one test is running.” Prefer a consolidated report that names completed deliverables, validation, and any decision needed.

## 8. Cross-Leader communication

Leaders may communicate directly. The Project Steward does not need to relay ordinary dependency information. Discuss API contracts, data models, network protocols, public types, interface dependencies, breaking changes, and development order.

After resolving a local interface issue, continue work. Escalate when the resolution changes project architecture, a public or shared schema, global conventions, roadmap scope, compatibility expectations, or ownership boundaries.

When two Leaders claim the same work:

1. identify the actual boundary;
2. determine whether one domain consumes the other;
3. prefer one clear owner over duplicated ownership;
4. let the Leaders propose a boundary;
5. escalate to the Steward if they cannot resolve it or the decision is project-wide.

## 9. Blocker handling

Classify an issue before escalating.

**Local issue:** ordinary compiler error, internal test failure, local refactor, or implementation uncertainty. Resolve it inside the Leader conversation.

**Cross-domain dependency:** contact the relevant Leader. Escalate only when the dependency cannot be resolved locally.

**Project-level blocker:** report immediately using:

```text
Blocker:
Impact:
What has been attempted:
Affected domains:
Decision required:
Recommended options:
```

## 10. Steward review delegation

The Steward should preserve reaction capacity. When independent checks are useful, delegate them to Steward-side Subagents while the Steward continues project coordination:

```text
Leader A Report
        ↓
Project Steward
        ├── Review Subagent A
        ├── process Leader B
        ├── Architecture Review Subagent
        └── continue project coordination
```

When review results return, the Steward chooses Accept, Accept with follow-up, Request changes, or Re-plan. Review Subagents advise; the Steward decides.

Match review depth to risk. Low-risk work needs deliverable, acceptance, and test checks. Medium-risk work also needs architecture interaction, regression, and roadmap checks. High-risk work may need independent reviews covering architecture, security, migrations, compatibility, integration, and rollback implications. Do not create review Subagents mechanically when there is nothing meaningful to review.

## 11. Project Registry boundary

The registry should describe each Leader's domain, current package, status, dependencies, pending decisions, and pending reviews. It should not contain file-level microtasks such as renaming a method or moving a helper; those belong in the Leader conversation.

## 12. Anti-patterns

Avoid Leader explosion, Steward micromanagement, chatty reporting, silent architecture drift, a Steward review bottleneck, and cross-Leader leakage into another domain's internal implementation. Keep implementation autonomy with the Leader that owns the domain, while escalating material shared changes.

The governing rule is:

```text
Steward thinks in roadmaps.
Leaders think in systems and milestones.
Subagents think in concrete tasks.
```
