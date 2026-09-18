# Coordination Templates

Use these structures when transferring work or decisions between hierarchy levels.

## 0. Role Declaration

Use at the start of a new agent conversation and whenever authority could be ambiguous.

```markdown
# Role Declaration

Role: <Project Steward / Leader / Subagent>
Project: <current project>
Parent Conversation: <conversation name or none>
Current Roadmap Package / Task: <one line>
Permitted Child: <Leader conversation in this project and/or Subagent in this conversation / None>
Creation Guard: <state the forbidden creation action for this role>
```

For the Project Steward, the permitted child may include both a justified same-project Leader conversation and Subagents inside the current Steward conversation.

For a Leader, the Creation Guard should say: `Do not create a new conversation, session, fork, or another Leader; create Subagents only inside this Leader conversation.`

## 1. Project Registry

```markdown
# Project Registry

## Project
<name>

## Current Phase
<phase>

## Roadmap
<high-level roadmap>

## Leaders

### <Leader Name>
Domain:
Current Roadmap Package:
Status:
Dependencies:
Pending Decisions:
Pending Reviews:

## Cross-Leader Dependencies
- ...

## Project-Level Decisions
- ...

## Pending Reviews
- ...

## Risks
- ...
```

Keep this project-level. Do not insert Leader microtasks.

## 2. Roadmap Package

Use when the Project Steward delegates work to a Leader.

```markdown
# Roadmap Package

## Objective
What project-level outcome must this stage achieve?

## Scope
What is included?

## Out of Scope
What should not be expanded into during this stage?

## Deliverables
- ...
- ...
- ...

## Acceptance Criteria
- ...
- ...
- ...

## Constraints
- architecture constraints
- compatibility requirements
- design rules
- technology restrictions

## Dependencies
- Leader / module / external dependency

## Shared Interfaces
Interfaces, schemas, protocols, or public contracts that may be affected.

## Reporting Trigger
Report when:
- the integrated milestone is complete; or
- an escalation condition occurs.

## Execution Location
The assigned Leader conversation in the current project. The Leader may create Subagents only inside that conversation.
```

Give the Leader the outcome and boundaries. Let the Leader choose its internal task breakdown.

## 3. Leader Report

Use for a consolidated report from a Leader to the Project Steward.

```markdown
# Leader Report

## Completed
What this stage completed.

## Deliverables
Code, files, interfaces, pull requests, designs, or other outputs.

## Validation
Tests, checks, reviews, or other evidence.

## Decisions
Important technical or design decisions made within authority.

## Problems
Known issues and their impact.

## Dependencies
Other Leaders, modules, or external dependencies involved.

## Need Decision
Items that require a Project Steward decision.

## Next
The next coherent stage, if already authorized.
```

Report a meaningful integrated batch. Do not use this template for every microtask.

## 4. Cross-Leader Request

Use when one Leader needs a contract or dependency decision from another Leader.

```markdown
# Cross-Leader Request

## From
<requesting Leader>

## To
<owning Leader>

## Context
Why the dependency is needed.

## Required Contract
API, event, schema, protocol, fields, behavior, or compatibility requirement.

## Constraints
Relevant deadlines, versions, or architecture constraints.

## Proposed Resolution
The smallest compatible proposal.

## Decision Needed By
<date or milestone>
```

Discuss the boundary and contract. Leave internal implementation choices to the owning Leader.

## 5. New Leader Recommendation

Use when a Leader believes a new durable work domain has appeared.

```markdown
# New Leader Recommendation

## Proposed Domain
<domain name>

## Project
<the same project that owns the Project Steward>

## Why Existing Leaders Are Insufficient
<boundary and context explanation>

## Durable Work Expected
<recurring roadmap or responsibilities>

## Scope
<what this Leader would own>

## Boundaries
<what remains with existing Leaders>

## Dependencies
<other Leaders or shared interfaces>

## Expected Duration
<ongoing / phase-based / approximate duration>

## Recommendation
<create a Leader inside the current project / reuse an existing Leader, with rationale>
```

The Project Steward makes the final decision. A request for parallelism alone is not sufficient evidence. If a new Leader is approved, create its conversation inside the same project as the Steward.

## 6. Review Request and Result

Use when the Steward delegates independent verification or records its outcome.

```markdown
# Review Request

## Subject
<Leader Report or milestone>

## Review Scope
- deliverables
- acceptance criteria
- tests and regressions
- architecture and interfaces
- security or data safety

## Evidence To Inspect
- ...

## Risk Level
<low / medium / high>

## Return
List findings by severity, cite evidence, and state whether the milestone is ready for acceptance.
```

```markdown
# Review Result

## Subject
<milestone>

## Scope Checked
<areas reviewed>

## Findings
- Severity:
  Finding:
  Evidence:
  Required Action:

## Validation Summary
<tests and checks>

## Recommendation
<accept / accept with follow-up / request changes / re-plan>
```

The review result is evidence for the Steward's decision, not a replacement for it.
