# SPEC template (canonical)

Copy between the markers during Phase 0, before interrogation. Replace every
placeholder; delete conditional sections only when the template permits it.
Express keeps the same contract but compresses prose.

<!-- TEMPLATE START -->

# Feature NNN — <title>

- Status: Draft | Approved | In implementation | Locally verified |
  Ready for integration | Integrated | Released | Declined
- Assurance: express | standard | deep
- Spec version: 1 · Created: <date> · Owner: <user>
- Base revision: <sha | greenfield>
- Raw ask: <user words, verbatim>
- Research: ./RESEARCH.md | none

## Problem and evidence

<Strongest-form problem statement: actor, current workflow, pain, why now.>

| Evidence | Class | Source | Limitation |
|---|---|---|---|
| <finding> | measured / observed / documented / inferred | <path:line / URL> | <cannot establish> |

**Case against, and why proceed:** <strongest don't-build / buy / smaller
validation slice argument and the decision answering it>.

## Outcome hypothesis

- Baseline: <value + source | not measured>
- Target: <product outcome | behavior-only change>
- Measurement: <method and window | not measured>
- Decision rule: <expand / revise / retire condition>

## Goals

- <observable product/system outcome>

## Non-goals

- <semantic exclusion>

## Global constraints

- <exact sourced or approved rule inherited by every implementation slice>

## User stories

1. **[P1]** As a <actor>, I want <capability>, so that <benefit>.
   Independent demonstration: <standalone observable value>.

## Acceptance criteria

- **AC-001** WHEN <trigger> THE SYSTEM SHALL <observable response>.
  Verify: test — <seam and assertion>.
- **AC-002** IF <error/abuse condition> THEN THE SYSTEM SHALL <safe response>.
  Verify: test — <seam and assertion>.

## Regression contract

<Only material behaviors with a credible causal path. `No material RC known`
requires searched surfaces and blind spots.>

- **RC-001** THE SYSTEM SHALL CONTINUE TO <existing behavior> WHEN
  <feature interaction>.
  Consumer: <class>. Verify: <test / command / probe>.

## Non-functional requirements *(conditional; mandatory sweep for deep)*

- **NFR-001** Under <condition>, THE SYSTEM SHALL <quantified result>.
  Verify: <test / command / probe>.

## Design decisions

- Approach: <chosen> over <rejected> because <evidence/reason>.
- Interfaces/data/state: <decision-level contracts; no implementation paths>.
- Test seams: <highest behavior seams; new seams and why>.

## Rollout and rollback *(required for medium/high risk)*

- Delivery mechanism / default: <flag, adapter, additive schema, etc.>
- Deployment order and mixed-version rule:
- Observability / decision threshold:
- Rollback or forward-fix boundary:
- Cleanup/contract trigger:

## Testing decisions

- Automated:
- Scripted/manual probes:
- Deliberately not tested: <why, owner, risk>

## Assumptions

<Only sourced, reversible, low-impact assumptions visible at approval.>

- <assumption> — source: <source>; reverse when: <trigger>

## Deferrals

- <item> — owner: <owner>; revisit when: <concrete trigger>

## Limitations

- <research/review/tooling blind spot and its consequence>

## Decision log (append-only)

| Date | Version | Entry | Approved by |
|---|---:|---|---|
| <date> | 1 | Draft created (assurance: <mode>) | — |
| <date> | 1 | Q: <question> → A: <answer> | <user/owner> |
| <date> | 1 | Approved version 1 · normative digest <normative-sha256> for implementation | <user/owner> |

<!-- TEMPLATE END -->
