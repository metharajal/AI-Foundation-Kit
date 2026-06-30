# Constitution

**Version:** 1.0.0
**Status:** Ratified
**Date:** 2026-06-30

## Preamble

This Constitution defines how AEOS is governed.

It establishes the principles, responsibilities, and decision-making framework that guide every project built within the AEOS ecosystem.

It does not describe tools.

It does not prescribe implementation details.

Those belong to Standards and Playbooks.

Instead, this Constitution defines the enduring principles that remain valid regardless of technologies, programming languages, frameworks, or AI models.

Every contributor—human or artificial intelligence—is expected to understand, respect, and apply this Constitution.

Every decision, every standard, every playbook, every project, and every architectural record derives its authority from this document.

This Constitution exists to ensure that AEOS remains coherent, trustworthy, auditable, and sustainable over time.

---

## Part I — Identity

## 1.1 What Is AEOS

AEOS is an AI Engineering Operating System.

AEOS is a sovereign software continuity platform.

It enables any person, team, or organization to discover, assess, recover, transform, continue, govern, operate, and learn from digital products — under technical, economic, and sovereign control.

It is not a software framework.

It is not a collection of templates.

It is not a development methodology.

It is not a simple AI assistant.

It is the engineering foundation from which digital products can be designed, governed, built, recovered, modernized, migrated, maintained, and evolved — regardless of their origin, their current state, or the tools used to create them.

Its purpose is to provide a shared engineering model that remains consistent across products, teams, technologies, and generations of AI systems.

Every project built within its scope inherits the principles defined by this Constitution.

## 1.2 The AI Engineering Operating System

AEOS defines a complete engineering operating model.

It provides a common language, a common governance model, and a common way of making engineering decisions.

Every project remains free to choose its implementation technologies.

No project is free to violate the engineering principles defined by this Constitution.

The Operating System is therefore independent of programming languages, frameworks, cloud providers, artificial intelligence models, and development tools.

Its stability comes from its principles, not from its technologies.

## 1.3 Scope of the Ecosystem

This Constitution governs AEOS and every project that explicitly adopts it.

Projects may extend this Constitution through Standards, Playbooks, RFCs, ADRs, and DECs.

They may not contradict its principles.

The ecosystem is designed to support multiple products, organizations, and engineering teams while preserving a single engineering philosophy.

Any project wishing to depart from these principles must explicitly declare itself outside the AEOS ecosystem.

## 1.4 Core Capabilities

AEOS provides eight core capabilities. Together, they cover the complete lifecycle of a digital product.

**Discover**
Understand what exists: repository structure, technology stack, dependencies, providers, generators, risks, and zones of unknown control.

**Assess**
Evaluate the current state: control map, security posture, sovereignty level, project maturity, and readiness to proceed.

**Recover**
Bring a fragile, captured, or ungoverned project back to a controlled, secure, portable, and governable state through a structured sequence of validated stages.

**Transform**
Modernize, migrate, refactor, or evolve a project toward a target architecture in controlled, tested, and reversible steps.

**Continue**
Resume or sustain development of a project under controlled AI assistance — local-first, with frontier AI reserved for genuinely complex tasks and subject to explicit human authorization.

**Govern**
Define, enforce, and maintain the engineering standards, architectural decisions, security policies, sovereignty policies, and AI usage policies that ensure long-term mastery of a project.

**Operate**
Monitor, audit, and maintain a project over time — detecting sovereignty drift, enforcing quality gates, and generating periodic evidence reports.

**Learn**
Accumulate validated knowledge from audits, decisions, and human-confirmed outcomes — in local, controlled memory — to make future operations faster, more accurate, and more consistent.

These eight capabilities are the official vocabulary for describing what AEOS does.
They are not sequential phases. Any project may engage any capability at any time, subject to the preconditions of the underlying engines and stages.

## 1.5 Platform Engines

AEOS delivers its capabilities through a set of platform engines. Each engine is a bounded, testable component with a defined scope, a read-only default behavior, and no autonomous side effects beyond its declared output.

The platform engines are:

- **Discovery Engine** — repository and project structure analysis
- **Assessment Engine** — control mapping, risk classification, maturity scoring
- **Recovery Engine** — stage-based sovereign recovery orchestration
- **Transformation Engine** — modernization, migration, and evolution planning
- **Continuation Engine** — local-AI-first development workflow management
- **Governance Engine** — governance document generation and enforcement
- **Operations Engine** — continuous audit, drift detection, and periodic reporting
- **Memory Engine** — local, validated knowledge storage and retrieval
- **Evidence Engine** — stage completion evidence management
- **AI Routing Engine** — local and frontier AI routing with human approval gates

Each engine is governed by the invariants defined in this Constitution. No engine may override the safety requirements defined in Part VI.

The engine catalog evolves through the Standards system. The principle of engine-based architecture — bounded scope, read-only default, evidence output — is constitutional and does not change.

## 1.6 The Three Level Systems

AEOS operates with three independent, orthogonal level systems. Each system measures a different dimension of an engineering project. None is a superset of the others.

**Action Levels** define what AEOS does and what human approval is required.
They range from Level 0 (read-only diagnosis, no gate required) to Level 5 (continuous operation with periodic human review). Higher action levels require progressively stronger human approval gates. All current AEOS capabilities operate at Action Levels 0 through 3 by default.

**Project Maturity Levels** measure the recovery state of a project.
A project progresses from `weak` (ungoverned, insecure, non-portable) through `partial`, `controlled`, and `portable`, to `sovereign` (fully controlled, secure, portable, and locally operable). Recovery is the process of advancing a project along this axis.

**Sovereignty Levels** measure the infrastructure dependency of a project.
They range from Level 1 (secured but cloud-dependent) to Level 5 (zero dependency on foreign platforms). A project may be at Sovereignty Level 3 while still at Project Maturity `partial`. These axes are independent.

The three level systems together provide a complete picture of a project's engineering state. A full assessment reports a value on each axis.

## 1.7 Platform Interfaces

All AEOS capabilities are accessible through four platform interfaces. Each interface exposes the same underlying engines with an interaction model appropriate to its context.

**CLI**
The primary interface. A command-line tool for engineers, scripts, and CI pipelines. Every capability is accessible without a graphical environment. The CLI is the reference implementation of all AEOS capabilities.

**API**
A programmatic interface for integration with other tools, systems, and automation workflows. The API exposes AEOS capabilities as structured services with defined inputs and outputs.

**Workspace**
A local graphical interface for non-terminal interaction. The Workspace enables review, validation, and visualization of AEOS outputs without requiring command-line access. It is designed for contexts where terminal interaction is impractical or inappropriate.

**Agents**
An autonomous execution interface. Specialized AI agents invoke engine capabilities in sequence, under human approval gates, to accomplish multi-step engineering tasks. Agents are subject to the governance rules defined in Part III.

All four interfaces enforce the same invariants. No interface bypasses the constraints defined by this Constitution.

The CLI is the authoritative interface. In any behavioral discrepancy between interfaces, the CLI behavior defines the correct behavior.

---

## Part II — Founding Principles

### 2.1 Engineering First

Engineering is the primary discipline of AEOS.

Technology choices are secondary.

Tools evolve.

Programming languages evolve.

Frameworks evolve.

Artificial intelligence evolves.

Engineering principles endure.

Every technical decision shall strengthen the long-term quality, maintainability, and understandability of the system before optimizing for speed, convenience, or novelty.

Engineering excellence is measured by the longevity of what is built, not by the speed at which it was produced.

### 2.2 Simplicity over Complexity

Complexity is a cost.

Every unnecessary abstraction, dependency, configuration, or process increases the long-term cost of a system.

Simplicity is not the absence of sophistication.

It is the deliberate elimination of everything that does not create lasting value.

When multiple solutions exist, the simplest solution that satisfies the requirements shall be preferred.

Complexity must always justify its existence.

### 2.3 Explicit over Implicit

Every important engineering decision shall be explicit.

Assumptions must be documented.

Architectural decisions must be recorded.

Standards must be written.

Processes must be understandable.

Knowledge must never exist only in people's minds.

A system that depends on implicit knowledge is a system that cannot scale.

Clarity always takes precedence over convenience.

### 2.4 Human Accountability

Responsibility cannot be delegated to software.

Artificial intelligence may assist, recommend, analyze, generate, or verify.

It shall never own accountability.

Every significant engineering decision must have a clearly identified human owner.

Automation reduces effort.

It never transfers responsibility.

Every contributor remains accountable for the work they approve, regardless of how it was produced.

### 2.5 Security by Design

Security is a design principle.

It is not a feature added at the end of a project.

Every architectural decision shall consider confidentiality, integrity, availability, and resilience from the beginning.

Systems shall minimize trust, reduce attack surfaces, and fail safely whenever possible.

Security is everyone's responsibility and shall be continuously reassessed as systems evolve.

### 2.6 Reproducibility

Every engineering environment shall be reproducible.

Every build, deployment, and development workflow shall be reconstructible from documented sources.

A project must never depend on undocumented local configurations or personal knowledge.

Any contributor shall be able to recreate the engineering environment using the documented process.

Reproducibility is the foundation of collaboration, automation, and long-term sustainability.

### 2.7 Traceability

Every significant engineering action shall be traceable.

Requirements, decisions, implementations, reviews, tests, and releases shall leave durable evidence.

History is an engineering asset.

It shall never be rewritten to hide mistakes.

Traceability enables accountability, auditability, continuous improvement, and trust.

A decision that cannot be traced shall be considered undocumented.

### 2.8 Continuous Improvement

Engineering is never finished.

Every system can be improved.

Every process can be refined.

Every mistake is an opportunity to strengthen the engineering system rather than assign blame.

Continuous improvement shall be driven by evidence, measurement, feedback, and learning.

Small, frequent improvements are preferred over infrequent large transformations.

The engineering system itself is subject to continuous improvement.

### 2.9 AI as an Engineering Partner

Artificial Intelligence is an engineering partner.

It expands human capabilities by accelerating exploration, implementation, verification, and documentation.

AI shall augment engineering judgment.

It shall never replace engineering responsibility.

Every AI contribution shall remain reviewable, understandable, and attributable.

The value of AI is measured by the quality of the engineering outcomes it enables, not by the amount of work it performs.

Human judgment remains the final authority in every engineering decision.

---

## Part III — Human + AI Collaboration

## 3.1 Collaboration Principle

Human and Artificial Intelligence are complementary contributors to the engineering process.

Humans provide purpose, judgment, ethics, and accountability.

Artificial Intelligence provides speed, consistency, exploration, and execution support.

Neither is sufficient alone.

The engineering system is designed to maximize the strengths of both while protecting against the weaknesses of each.

Human–AI collaboration is therefore a foundational engineering capability rather than an optional productivity technique.

---

## 3.2 Human Responsibilities

Humans define objectives.

Humans establish priorities.

Humans approve architectural decisions.

Humans validate engineering outcomes.

Humans remain accountable for every accepted change.

No engineering decision becomes authoritative until a human explicitly accepts responsibility for it.

Engineering ownership is inseparable from human accountability.

---

## 3.3 AI Responsibilities

Artificial Intelligence assists engineering work.

It may generate code, documentation, tests, designs, analyses, proposals, and reviews.

It may identify inconsistencies, suggest improvements, detect risks, and automate repetitive activities.

AI contributes knowledge and execution.

It does not define organizational intent.

Its contributions remain proposals until validated by a human.

---

## 3.4 AI Autonomy Boundaries

Artificial Intelligence shall never perform irreversible engineering actions without explicit human authorization.

This includes, but is not limited to:

* merging protected branches;
* approving architectural decisions;
* deploying production systems;
* managing secrets or credentials;
* accepting security exceptions;
* modifying governance documents.

Autonomy is granted deliberately.

Responsibility is never delegated implicitly.

---

## 3.5 Shared Accountability

Engineering quality is a shared objective.

Engineering responsibility is not.

AI may contribute to an outcome.

Humans remain accountable for approving that outcome.

Every accepted contribution shall have an identifiable human owner.

This principle applies regardless of the tools, models, or automation involved.

Shared collaboration never implies shared accountability.

---

## Part IV — Governance

## 4.1 Governance Model

AEOS is governed through explicit and documented decisions.

Authority exists to preserve coherence, not hierarchy.

Governance provides a framework for making decisions consistently across projects while allowing teams to remain autonomous in their implementation choices.

Every governance decision shall be transparent, documented, and reviewable.

No undocumented governance rule shall be considered valid.

---

## 4.2 Decision Framework

Engineering decisions are classified according to their impact.

Operational decisions may be taken autonomously.

Architectural decisions require documented justification.

Foundational decisions require formal review and approval.

The higher the impact of a decision, the higher the level of documentation, review, and consensus required.

Every significant decision shall leave a permanent engineering record.

---

## 4.3 Conflict Resolution

Technical disagreement is a normal part of engineering.

Conflicts shall be resolved through evidence, experimentation, documentation, and engineering reasoning rather than authority or personal preference.

When consensus cannot be reached, the designated decision owner assumes responsibility for the final decision.

Once a decision is made, the team commits to its implementation until new evidence justifies reconsideration.

---

## 4.4 Authority & Ownership

Every engineering artifact shall have a clearly identified owner.

Ownership creates accountability.

Ownership does not create absolute authority.

Every owner remains accountable to the principles defined by this Constitution.

No contributor—human or artificial intelligence—may override the Constitution, regardless of role, seniority, or technical expertise.

The Constitution is the highest engineering authority within AEOS.

---

## Part V — Engineering Principles

### 5.1 Design Philosophy

AEOS is designed for durability of ownership, not speed of generation.

Every engine, every capability, and every interface is designed to remain correct, understandable, and maintainable as the system evolves.

Complexity is introduced only when simpler alternatives have been considered and found insufficient. Every abstraction must justify its cost.

Every behavioral boundary is explicit. Side effects are documented. Invariants are expressed in code and verified by tests.

Read-only is the design default. An engine that reads before it acts is safer than one that acts before it reads. The read-only constraint is code-enforced, not merely conventional.

Composability is a design requirement. Every capability must be accessible as a standalone operation. No capability is locked into a specific workflow or execution sequence.

Evidence production is a design requirement. Every operation that produces a result must produce that result in a form that is inspectable, serializable, and auditable.

### 5.2 Code Quality

Code quality in AEOS is enforced through automated gates, not aspirational guidelines.

All AEOS code must satisfy the following before being considered complete:

**Static analysis** — Code must conform to the configured linting and formatting rules with no suppressed warnings beyond documented exceptions.

**Type checking** — Code must pass strict static type checking. Every public function signature must be fully typed. Type errors may not be suppressed without documented justification.

**Tests** — All logic must have corresponding tests. The test suite must pass before any merge to the main branch. No code path that enforces a declared invariant may lack a test.

**CI gate** — All quality checks must run automatically on every pull request. No merge is permitted while the gate is failing.

These requirements apply to AEOS itself and to every Standard that AEOS-governed projects adopt.

A passing CI gate is a necessary condition, not a sufficient one. Engineering judgment remains required to evaluate whether the test suite adequately covers the system's behavior.

### 5.3 Architecture

AEOS architecture is organized around capabilities and engines.

Engines are the bounded, testable units of AEOS functionality. Each engine has a single, clearly defined scope. Dependencies between engines are explicit and directed. Circular dependencies between engines are not permitted.

Every engine enforces its safety invariants internally. Safety is not delegated to the calling layer.

Every architectural decision that affects the AEOS platform must be documented as an Architecture Decision Record in the project's ADR directory.

AEOS is infrastructure-independent. No engine requires a cloud account, a hosted service, or an external network connection by default. Local execution is always the baseline.

Portability is an architectural requirement. Every AEOS scaffold, every generated document, and every configuration file must be usable on any machine with the documented runtime prerequisites.

Architecture evolves through evidence. No architectural change is made to optimize for a hypothetical future requirement. Changes are made to address demonstrated needs.

### 5.4 Testing & Reliability

Testing is a first-class engineering discipline.

Every capability must have:

**Unit tests** covering the logic of each engine component in isolation. Unit tests must not depend on network access, filesystem state beyond the test fixture, or external services.

**Integration tests** verifying the behavior of engines in combination. Integration tests may use controlled filesystem fixtures but must not require external services.

**Invariant tests** explicitly verifying that the safety constraints defined in Section 6.2 are enforced. The read-only invariant, the no-secrets invariant, and the applied-false invariant each require a dedicated test.

A failing test is a defect, not a warning. Failed tests are not merged.

Reliability means that every operation produces consistent, reproducible results given the same inputs. Non-deterministic behavior requires explicit documentation of the source of variance.

Tests are the executable specification of the system. When documentation and tests disagree, the tests define the behavior.

### 5.5 Documentation

Documentation is a first-class engineering artifact.

Every project governed by AEOS must maintain the following governance documents. These are outputs of the engineering process, not afterthoughts.

**Required governance documents:**

| Document | Purpose |
|---|---|
| `ARCHITECTURE.md` | Structural overview: components, dependencies, data flows, decisions |
| `aeos.toml` | AEOS configuration and project registration |
| `docs/DECISIONS.md` | Architecture decision log: context, options, rationale, consequences |
| `docs/SECURITY.md` | Security policy: threat model, baseline, incident history |
| `docs/SOVEREIGNTY.md` | Sovereignty posture: provider inventory, dependency levels, exit strategies |
| `docs/AI-DEVELOPMENT-POLICY.md` | AI usage rules: local vs. frontier boundaries, forbidden contexts, approval process |
| `docs/features/AEOS-RECLAIM-RECOVERY.md` | Recovery roadmap when applicable: stages, progress, pending gates |

These documents are living artifacts. They must be updated when the engineering reality they describe changes.

A governance document that no longer reflects the current state of the project is an active liability, not passive documentation.

AEOS applies this standard to itself. The AEOS project must maintain all required governance documents.

---

## Part VI — Quality & Safety Principles

### 6.1 Quality Standards

Quality in AEOS is defined as the degree to which a system meets its stated requirements and the implicit requirements of its operational context — maintainability, understandability, portability, and sovereignty.

Quality is not a layer added at the end. It is a property verified continuously throughout development and operation.

A project operating under AEOS quality standards must satisfy:

- All code quality gates defined in Section 5.2 for any code it contains
- A documented architecture before any feature is built
- A test baseline before any production deployment
- A CI quality gate before any merge to the main branch
- Evidence of recovery progress appropriate to its risk level and sovereign posture

Quality gates are binary: they pass or they do not. There is no partial compliance.

### 6.2 Safety Requirements

Safety in AEOS is defined as the guarantee that AEOS operations do not produce irreversible harm without explicit human authorization.

The following safety requirements are absolute. They cannot be overridden by configuration, by agent behavior, or by any interface:

**No secret exposure.** AEOS never reads, displays, logs, or transmits the value of a secret. Variable names may be referenced. Values never appear in any output, log, or transmitted context.

**No unauthorized modification.** `read_only: true` is the default state of all diagnostic commands. No file in the audited project is modified without explicit intent and explicit command scope.

**No applied state without intent.** `applied: false` is the invariant of all read-only commands. Generated SQL, generated code, and generated configurations are proposals until explicitly applied through a Level 3 or higher action.

**No silent frontier escalation.** The AI Routing Engine does not escalate to frontier AI without explicit human authorization. When `require_human_approval = true`, the system stops and asks; it never silently escalates.

**No destructive action without gate.** No deletion, rotation, migration, or irreversible operation proceeds without a documented human approval step defined in the relevant Playbook.

**No autonomous production change.** No agent, no engine, and no interface may apply changes to a production system without explicit human confirmation at Action Level 4.

These requirements are code-enforced and test-verified. They are not conventions.

### 6.3 Risk Management

Risk management in AEOS follows an assess-before-act model. Every capability that may have side effects must follow this sequence:

1. **Diagnose** — assess the current state before proposing any action (Action Level 0)
2. **Plan** — generate a structured plan before executing any step (Action Level 1)
3. **Prepare** — generate files and configurations for human review before applying (Action Level 2)
4. **Gate** — define a rollback path before executing any irreversible step
5. **Evidence** — produce evidence at every step before declaring completion
6. **Approve** — require explicit human approval before crossing an irreversible boundary (Action Level 3+)

Risk is classified by action level (Section 1.6). Level 0–2 operations are non-destructive by definition. Level 3–5 operations require progressively stronger human approval gates and documented rollback paths.

No risk management step may be skipped in the interest of speed or convenience.

### 6.4 Incident Response & Post-Mortems

When an AEOS operation produces an unexpected or harmful result, the following principles govern the response:

**Investigate before acting.** The cause of the incident must be understood before remediation begins. Premature remediation may destroy evidence or worsen the situation.

**Preserve evidence.** All logs, audit records, and memory records related to the incident must be retained and not modified.

**Document the incident.** The incident, its cause, its timeline, and its resolution must be recorded in the project's `docs/DECISIONS.md` or in a dedicated incident record.

**Learn from the incident.** The lessons must be incorporated into the project's tests, standards, or governance documents before the incident is considered closed.

**Do not assign blame.** Incidents are system failures. The investigation must focus on what in the engineering system allowed the incident to occur.

No incident record is ever deleted or altered. History is an engineering asset.

---

## Part VII — Standards & Playbooks System

### 7.1 Standards Hierarchy

AEOS operates with a layered authority hierarchy. Each layer derives its authority from the layer above it.

```
MANIFESTO
    └── CONSTITUTION
            ├── Standards
            │       └── Playbooks
            │               └── ADRs (Architecture Decision Records)
            ├── DECs (Engineering Decision Records)
            └── RFCs (Requests for Comments — proposals only)
```

**MANIFESTO** — The philosophical foundation. It declares convictions, not rules. Every layer derives legitimacy from its convictions. The MANIFESTO does not expire and does not bend to convenience.

**CONSTITUTION** — This document. Defines engineering principles, identity, safety requirements, and governance. Every Standard and Playbook must be consistent with this Constitution.

**Standards** — Documented engineering requirements applicable to all projects within the AEOS ecosystem. Standards define what must be done. They are prescriptive and enforceable.

**Playbooks** — Step-by-step operational guides for executing specific engineering workflows under AEOS. Playbooks define how to do it. They implement one or more Standards.

**ADRs (Architecture Decision Records)** — Project-specific records of significant architectural decisions: context, options considered, decision taken, rationale, and consequences.

**DECs (Engineering Decision Records)** — Platform-level engineering decisions that affect AEOS itself, not bound to a specific project.

**RFCs (Requests for Comments)** — Proposals for changes to Standards, Playbooks, or this Constitution. An RFC is not a decision. It becomes a Standard or Constitutional amendment only after ratification.

**Resolution rule:** No Standard may contradict this Constitution. No Playbook may contradict the Standard it implements. In any conflict, the higher layer prevails.

### 7.2 Playbook Structure

Every AEOS Playbook must contain the following sections:

**Purpose** — what the Playbook enables and when it applies.

**Preconditions** — the state required before the Playbook begins. Preconditions that are not met must prevent the Playbook from starting.

**Steps** — an ordered sequence of actions with defined inputs, outputs, and evidence requirements for each step.

**Human gates** — the points at which human approval is required before proceeding. Each gate must specify what the human is approving and what the consequence of refusal is.

**Evidence** — the artifacts produced at each step that prove the step has been completed. Evidence must be inspectable and auditable.

**Rollback** — the procedure to reverse each applied action. A Playbook step that applies an irreversible action without a defined rollback procedure is incomplete and may not be published.

**References** — links to the Standard(s) the Playbook implements and to any related ADRs or DECs.

### 7.3 Adoption & Compliance

A project adopts the AEOS ecosystem by declaring itself within AEOS scope through its `aeos.toml` configuration file.

Adoption implies:
- Acceptance of this Constitution and all active Standards
- Commitment to maintaining the governance documents defined in Section 5.5
- Willingness to undergo periodic AEOS audit and to act on findings

Compliance is verified through AEOS audit capabilities. A project is compliant when:
- Its governance documents are present and reflect the current engineering state
- Its code quality gates are active and passing
- Its security invariants are maintained
- Its sovereignty posture is documented and consistent with its stated level

Compliance is not a one-time certification. It is a continuous state maintained through ongoing engineering practice.

A project that adopts AEOS but does not maintain compliance is drifting from its own stated standards. The AEOS audit system exists to make this drift visible.

### 7.4 Maintenance & Review

Standards are maintained through the RFC process defined in Section 7.1.

A Standard may be updated when:
- New engineering evidence warrants a change
- The AEOS platform evolves in a way that makes the Standard obsolete or incorrect
- An RFC proposing the change has been ratified through the process defined in Part VIII

A Standard is never deleted — it is deprecated. Deprecated Standards must document the reason for deprecation and the replacement, if any.

Playbooks are reviewed whenever the Standard they implement changes. A Playbook that no longer matches its Standard must be updated before the next use.

The Standards system is itself subject to the Continuous Improvement principle defined in Section 2.8.

---

## Part VIII — Constitution Evolution

### 8.1 Amendment Process

This Constitution may be amended only through a formal RFC process.

An RFC proposing a Constitutional amendment must:

1. Identify the specific section(s) to be amended, with the current text and the proposed replacement
2. State the reason for the amendment and the engineering evidence supporting it
3. Demonstrate that the proposed change is consistent with the MANIFESTO
4. Have been open for review for the minimum review period defined in Section 8.3

An RFC proposing to remove or weaken any founding principle in Part II must additionally:
- Demonstrate that the principle as written contradicts a more fundamental principle from the MANIFESTO
- Propose a replacement that preserves the underlying intent of the weakened principle

No amendment may contradict the MANIFESTO. The MANIFESTO is the supreme document.

### 8.2 Versioning

This Constitution is versioned using semantic versioning (MAJOR.MINOR.PATCH).

- **MAJOR version**: any change to Part I (Identity), Part II (Founding Principles), Part III (Human + AI Collaboration), or Part IV (Governance) — these define the permanent character of AEOS
- **MINOR version**: any change to Part V (Engineering Principles), Part VI (Quality & Safety), or Part VII (Standards System)
- **PATCH version**: corrections of errors, ambiguities, or formatting issues that do not alter the meaning of any section

The current version is declared in the document header.

Every change to this Constitution produces a new version. The version history is maintained in the AEOS ADR system.

### 8.3 Review Cadence

This Constitution is reviewed at regular intervals and whenever a significant decision changes the AEOS platform identity, capabilities, or standards.

A standard review examines:
- Whether new capabilities, engines, or interfaces have been added and require Constitutional recognition
- Whether any section has become inconsistent with current engineering practice or with the MANIFESTO
- Whether any Standard or Playbook has surfaced a gap or inconsistency in the Constitution

The review produces either:
- A documented declaration that no amendment is required
- One or more RFCs proposing specific amendments

A Constitution that is not periodically reviewed will diverge from the engineering reality it governs — and a governance document that does not reflect reality governs nothing.

### 8.4 Ratification & Approval

A Constitutional amendment is ratified when all of the following conditions are met:

1. The RFC has been open for review for the minimum review period
2. No unresolved substantive objections remain open
3. The designated authority has provided explicit written approval
4. The new version has been committed to the main branch with a signed commit and a version tag

An amendment that has not been ratified through this process is not valid.

The Constitution is the highest engineering authority within AEOS. No role, no seniority level, and no technical argument overrides a ratified Constitutional provision without following the amendment process defined in this Part.

The authority of the Constitution comes from its ratification, not from its age. A newer ratified amendment always supersedes an older provision.
