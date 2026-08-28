# Exact Isolated-Research Prompt Protocol

## Reconstruction rule

The exact dispatch text is recorded compositionally so repeated instructions are not copied nineteen times. For FND-01 through AI-02, concatenate **Common prefix**, the subject's first four block lines, and **Protocol A suffix**, separated by one blank line. For GOV-01 through GOV-03, concatenate **Common prefix**, all five research lines in the subject block, and **Protocol B suffix**, separated by one blank line. In either suffix, replace `OUTPUT_PATH` in instruction 7 with the literal path in the subject block; the `OUTPUT_PATH:` metadata line itself was not sent. The two suffixes use the same research criteria with minor editorial wording differences, retained here rather than silently normalized.

No orchestration conversation or other research was inherited (`fork_turns: none`). Every dispatch used `model: gpt-5.6-luna` and `reasoning_effort: xhigh`.

## Common prefix

```text
You are the sole isolated research subagent for one subject in a 2026 university-grade quality-engineering manual. Do not delegate or inspect other agents’ work.
```

## Protocol A suffix

```text
NEUTRAL FRAMING: Evaluate definitions, evidence, disagreements, limitations, and applicability without assuming that any named standard, method, or organizational model is universally effective.

STANDARDIZED RESEARCH INSTRUCTIONS:
1. Browse and research primary sources. Apply this strict hierarchy: Tier 1—peer-reviewed papers from ACM Digital Library or IEEE Xplore, formal standards from ISO/IEC/IEEE or NIST, and university/CMU SEI/MIT/Stanford research or courseware. Tier 2—industry consensus specifications, official framework architecture documentation, and validated vendor-neutral whitepapers. Prohibited—SEO marketing blogs, unverified Medium-style posts, content farms, and commercial promotional material.
2. Prefer authoritative sources current through 2026, but include older seminal work when foundational. Record the actual publication year; never relabel an older work as 2026.
3. Use at least 8 strong sources, with at least 5 from Tier 1 when the literature permits. Cross-check pivotal claims. Distinguish normative requirements from guidance, empirical findings, and your own inference.
4. Every evidence item must have a stable DOI or direct authoritative URL. Exact quotations must be verified against the source, include enough local context in the excerpt field to be intelligible, and contain no more than 20 verbatim words from any one source. Do not invent quotations or citation metadata.
5. Provide concrete theory, engineering mechanisms, decision criteria, tradeoffs, implementation detail where within scope, evaluated failure modes, and a three-stage maturity progression. Identify evidence gaps and contested claims.
6. Return valid JSON only, encoded as UTF-8, following the schema below. Strings may contain Markdown. Map a peer-reviewed ACM paper to ACM, peer-reviewed IEEE paper to IEEE, ISO/NIST/W3C/industry consensus specifications to Formal_Standard, and university or SEI sources to University_Courseware. Use the actual year integer in `year`.
7. Also write the identical JSON deliverable to `OUTPUT_PATH` using apply_patch. Do not modify any other file.

DELIVERABLE SCHEMA:
{
  "subject_id": "STRING",
  "subject_title": "STRING",
  "theoretical_foundations": "DETAILED_SYNTHESIS",
  "practical_architecture_and_implementation": "DETAILED_SPECS",
  "primary_evidence": [
    {
      "source_title": "STRING",
      "authors_or_institution": "STRING",
      "year": 2026,
      "source_type": "ACM | IEEE | ISO | University_Courseware | Formal_Standard",
      "doi_or_url": "STRING",
      "verbatim_excerpt": "EXACT_QUOTATION_WITH_CONTEXT_MAX_20_WORDS_PER_SOURCE",
      "analytical_interpretation": "HOW_THIS_APPLIES_TO_2026_SDLC"
    }
  ],
  "failure_modes_and_antipatterns": ["LIST_OF_EVALUATED_FAILURE_MODES"],
  "maturity_matrix": {
    "foundational": "STRING",
    "advanced": "STRING",
    "expert_2026": "STRING"
  }
}
```

`OUTPUT_PATH` above is replaced in the dispatched text by the literal backtick-delimited absolute path listed in the relevant subject block; it is not sent as a placeholder. The `OUTPUT_PATH:` metadata line in a subject block is part of this audit record and is not separately sent.

## Protocol B suffix

```text
STANDARD RESEARCH INSTRUCTIONS:
1. Use sources in this strict priority order. Tier 1: peer-reviewed ACM/IEEE papers; formal ISO/IEC/IEEE and NIST standards/publications; university courseware or research-lab publications (for example CMU SEI, MIT, Stanford). Tier 2: industry-consensus specifications, official framework architecture documentation, and validated vendor-neutral whitepapers. Do not use SEO marketing blogs, Medium-style posts, or commercial promotional material.
2. Search for the strongest primary evidence available through 2026, but preserve each source’s actual publication year. Do not label an older source as 2026. Clearly distinguish normative requirements, empirical findings, and your synthesis or inference.
3. Include at least 8 primary-evidence entries and at least 5 Tier-1 entries when available. Cross-check consequential claims across independent sources.
4. Every evidence entry must provide a stable DOI or direct primary URL and a verified exact excerpt of no more than 20 words. Never invent a quotation, DOI, URL, author, title, result, or standard requirement.
5. Cover theory, mechanisms, architecture, implementation controls, decision criteria, trade-offs, limitations, failure modes, maturity levels, and unresolved gaps. Make the synthesis concrete enough for a senior enterprise QA department.
6. Return valid JSON only matching the schema below. Map source types to the allowed enum; use Formal_Standard for NIST and official framework/specification sources when no narrower enum applies. Use the source’s actual integer year.
7. Also write the identical JSON deliverable to OUTPUT_PATH using apply_patch only. Modify no other file.

DELIVERABLE SCHEMA:
{
  "subject_id": "STRING",
  "subject_title": "STRING",
  "theoretical_foundations": "DETAILED_SYNTHESIS",
  "practical_architecture_and_implementation": "DETAILED_SPECS",
  "primary_evidence": [
    {
      "source_title": "STRING",
      "authors_or_institution": "STRING",
      "year": 2026,
      "source_type": "ACM | IEEE | ISO | University_Courseware | Formal_Standard",
      "doi_or_url": "STRING",
      "verbatim_excerpt": "EXACT_QUOTATION_WITH_CONTEXT",
      "analytical_interpretation": "HOW_THIS_APPLIES_TO_2026_SDLC"
    }
  ],
  "failure_modes_and_antipatterns": ["LIST_OF_EVALUATED_FAILURE_MODES"],
  "maturity_matrix": {
    "foundational": "STRING",
    "advanced": "STRING",
    "expert_2026": "STRING"
  }
}
```

## Subject blocks

### FND-01

```text
SUBJECT_ID: FND-01
SUBJECT_TITLE: Quality Theory, Quality Models, Testing Standards, and Evidence
SCOPE DEFINITION: Research the conceptual foundations of software quality and verification/validation; quality attributes and models; test-process, documentation, and terminology standards, especially ISO/IEC 25010 and ISO/IEC/IEEE 29119; the relationship among quality risk, assurance, testing, and evidence. Exclude detailed test-design techniques, pipeline implementation, non-functional test execution, production experimentation, AI-system evaluation, and departmental economics.
STRUCTURAL OBJECTIVE: Produce a self-contained research module that can ground the vocabulary, conceptual model, standards map, limitations, and 2026 enterprise implications of the manual.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\FND-01.json
```

### FND-02

```text
SUBJECT_ID: FND-02
SUBJECT_TITLE: Specification-Based Test Design and Behavioral Modeling
SCOPE DEFINITION: Research formal and systematic black-box test-design techniques: equivalence partitioning, boundary-value analysis, decision tables, cause-effect graphs, classification trees, use-case/scenario testing, state-transition models, and coverage criteria for those models. Include derivation procedures, adequacy logic, oracle construction, and worked engineering patterns. Exclude combinatorial interaction testing, mutation testing, search-based testing, static program analysis, CI execution architecture, non-functional testing, and organizational governance.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining theoretical foundations, rigorous test-derivation workflows, artifact formats, selection criteria, limitations, and 2026 enterprise applications.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\FND-02.json
```

### FND-03

```text
SUBJECT_ID: FND-03
SUBJECT_TITLE: Combinatorial, Model-Based, Search-Based, Mutation, and Coverage-Adequacy Methods
SCOPE DEFINITION: Research combinatorial interaction testing and covering arrays; model-based test generation from behavioral or formal models; search-based software testing; mutation analysis; structural coverage and adequacy criteria; and the coupling-effect/subsumption assumptions used to reason about test strength. Include mathematics, algorithms, generation constraints, tool-agnostic workflows, and empirical limitations. Exclude basic specification-based techniques, static program analysis, production AI/LLM evaluation, CI orchestration, and organizational metrics.
STRUCTURAL OBJECTIVE: Produce a self-contained module that explains advanced test-generation and adequacy theory, operational algorithms, decision criteria, failure modes, and 2026 enterprise use.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\FND-03.json
```

### SL-01

```text
SUBJECT_ID: SL-01
SUBJECT_TITLE: Static Program Analysis and Formal Verification
SCOPE DEFINITION: Research static verification of software without executing the target program: parsing and AST/IR inspection, type and effect systems, control/data-flow analysis, taint analysis, abstract interpretation, model checking, symbolic and concolic execution, weakest preconditions, SMT/SAT solving, proof assistants, and soundness/precision/scalability tradeoffs. Include integration points and evidence semantics. Exclude runtime security scanning, executable API/consumer contracts, property-based runtime testing, CI fleet orchestration, and governance economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining theoretical foundations, analysis architecture, solver workflows, finding triage, assurance limits, adoption criteria, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\SL-01.json
```

### SL-02

```text
SUBJECT_ID: SL-02
SUBJECT_TITLE: Executable Specifications, Contract Testing, Property-Based Testing, and Developer Feedback
SCOPE DEFINITION: Research executable interface and behavioral specifications; schema validation with OpenAPI/AsyncAPI or equivalent consensus specifications; consumer-driven and provider contract testing; compatibility and versioning; property-based and generative testing; metamorphic relations when used as developer-loop properties; example-based TDD/BDD as feedback mechanisms; and IDE, pre-commit, and local test-loop architecture. Exclude general static program analysis, organization-wide CI fleet orchestration, runtime production monitoring, AI-system evaluation, and governance economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining contract and property semantics, generator/shrinker design, compatibility architecture, developer-loop implementation, evidence limits, failure modes, and 2026 enterprise adoption.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\SL-02.json
```

### CT-01

```text
SUBJECT_ID: CT-01
SUBJECT_TITLE: Hermetic Continuous-Test Infrastructure and Ephemeral Environments
SCOPE DEFINITION: Research reproducible and hermetic builds/tests; dependency and network isolation; artifact provenance; ephemeral environment design with containers, virtual machines, or equivalent isolation; environment orchestration; service virtualization and test doubles; fixture lifecycle; clock, randomness, locale, and concurrency controls; infrastructure-as-code validation; and integration of the test harness with CI/CD. Exclude regression-test selection, prioritization, parallel scheduling algorithms, flaky-test classification, production release experimentation, and detailed NFR test methods.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining continuous-test infrastructure architecture, reproducibility controls, ephemeral topology, evidence capture, tradeoffs, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\CT-01.json
```

### CT-02

```text
SUBJECT_ID: CT-02
SUBJECT_TITLE: Test Selection, Prioritization, Parallelism, and Suite Trust
SCOPE DEFINITION: Research regression-test selection and test impact analysis; safe versus heuristic selection; test prioritization; change, dependency, coverage, and history models; execution scheduling and parallel sharding topologies; resource/contention-aware execution; flaky-test definitions, detection algorithms, classification, quarantine, retry semantics, and repair; and quantitative suite-trust measures. Exclude ephemeral environment construction, hermetic build design, detailed NFR methods, production rollout analysis, and organizational economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining selection and scheduling algorithms, evidence tradeoffs, flake statistics, parallel execution architecture, trust controls, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\CT-02.json
```

### NFR-01

```text
SUBJECT_ID: NFR-01
SUBJECT_TITLE: Performance, Scalability, and Capacity Assurance
SCOPE DEFINITION: Research workload modeling; latency, throughput, utilization, saturation, and queueing theory; load, stress, spike, breakpoint, volume, and endurance/soak testing; coordinated-omission and open/closed workload issues; statistical analysis of tails; capacity planning; performance regression detection; and performance test environment and observability requirements. Exclude fault-injection/chaos engineering, disaster recovery, security performance, general CI orchestration, and production canary/RUM decision systems.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining performance theory, workload and experiment design, capacity mathematics, instrumentation, acceptance analysis, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\NFR-01.json
```

### NFR-02

```text
SUBJECT_ID: NFR-02
SUBJECT_TITLE: Reliability, Resilience, Chaos, and Recovery Assurance
SCOPE DEFINITION: Research reliability theory and reliability-growth modeling; fault/error/failure semantics; resilience, availability, graceful degradation, redundancy, and fault containment; fault injection and chaos engineering with steady-state hypotheses and blast-radius controls; recovery, backup/restore, failover, disaster recovery, RTO/RPO, game days, and evidence of recovery correctness. Exclude nominal performance/capacity testing, security penetration methods, field observability architecture, and progressive-delivery canary analysis.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining reliability and recovery mathematics, experiment architecture, safe fault injection, recovery validation, evidence limits, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\NFR-02.json
```

### NFR-03

```text
SUBJECT_ID: NFR-03
SUBJECT_TITLE: Security Assurance Across the SDLC
SCOPE DEFINITION: Research threat-informed security testing; abuse/misuse cases; secure-design and verification controls; SAST, DAST, IAST, software-composition analysis, secret and configuration scanning; coverage-guided and protocol fuzzing; penetration testing and adversarial validation; vulnerability severity/exploitability triage; software-supply-chain verification; and evidence integration with NIST SSDF and related formal guidance. Exclude general static correctness theory, performance/reliability testing, broad regulatory governance, and test-data privacy operations.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining layered security-assurance architecture, technique semantics and limits, fuzzing and dynamic-analysis workflows, risk triage, evidence, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\NFR-03.json
```

### NFR-04

```text
SUBJECT_ID: NFR-04
SUBJECT_TITLE: Accessibility, Usability, Compatibility, and Internationalization Assurance
SCOPE DEFINITION: Research accessibility conformance and usability evaluation, especially WCAG 2.2 and ISO/IEC 40500:2025; automated versus manual accessibility testing; assistive-technology and disability-inclusive testing; keyboard, focus, semantics, contrast, authentication, cognitive and mobile needs; human-subject usability methods; browser/device/platform compatibility; localization and internationalization behavior including Unicode, locale, bidi, calendars, formatting, and text expansion. Exclude performance, security penetration, product-data integrity, and regulatory governance beyond what is needed to interpret applicable accessibility standards.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining normative criteria, evaluation architecture, automation limits, representative human testing, compatibility/i18n matrices, evidence, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\NFR-04.json
```

### NFR-05

```text
SUBJECT_ID: NFR-05
SUBJECT_TITLE: Data Quality, Integrity, Persistence, and Migration Assurance
SCOPE DEFINITION: Research product-data correctness and persistence behavior: data-quality dimensions and ISO/IEC 25012; schema and domain constraints; transactions, isolation, consistency, concurrency anomalies, idempotency, and event ordering; database and storage verification; ETL/ELT and analytical-pipeline correctness; lineage and reconciliation; schema/data migrations, backfills, roll-forward/rollback, and data-loss detection. Exclude test-data provisioning and privacy governance, general disaster-recovery exercises, performance capacity, and business intelligence economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining data-quality theory, transactional and pipeline test architecture, integrity oracles, migration protocols, reconciliation mathematics, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\NFR-05.json
```

### SR-01

```text
SUBJECT_ID: SR-01
SUBJECT_TITLE: Observability-Driven Testing and Field Diagnosability
SCOPE DEFINITION: Research logs, metrics, traces, profiles, events, and causal correlation as quality evidence; OpenTelemetry data/context/semantic conventions; distributed tracing and baggage; service-level indicators and runtime invariants; observability requirements and testing instrumentation itself; CI/test observability; trace-based test generation or verification; field diagnosability and incident learning. Exclude synthetic monitoring, canary/progressive-delivery decisions, traffic shadowing, RUM product feedback, detailed performance/chaos methods, and organizational incident economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining observability semantics, telemetry architecture, instrumentation validation, invariant and trace-based testing, evidence limits, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\SR-01.json
```

### SR-02

```text
SUBJECT_ID: SR-02
SUBJECT_TITLE: Progressive Delivery, Synthetic Monitoring, Traffic Shadowing, and RUM Feedback
SCOPE DEFINITION: Research production quality controls after preproduction testing: feature flags and progressive exposure; canary and control cohorts; statistical canary analysis and rollback; blue/green and staged deployment; synthetic monitoring; traffic mirroring/shadowing and differential response analysis; real-user monitoring (RUM), field quality signals, feedback to test models, and privacy-aware sampling. Exclude telemetry instrumentation internals, preproduction performance/chaos methods, AI-system evaluation, and governance economics.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining production-experiment architecture, cohort/statistical validity, shadow safety, synthetic/RUM controls, rollback evidence, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\SR-02.json
```

### AI-01

```text
SUBJECT_ID: AI-01
SUBJECT_TITLE: Evaluation and Assurance of ML, LLM, and Nondeterministic Systems
SCOPE DEFINITION: Research test/evaluation/verification/validation of statistical ML, generative AI, and LLM applications; nondeterministic output and repeated-sampling design; task and risk taxonomies; benchmark construction, contamination, leakage, representativeness, and versioning; statistical metrics and uncertainty; robustness, distribution shift, drift, fairness, privacy, security, toxicity/harm, calibration, and abstention; human evaluation and LLM-as-judge validity; red teaming and production evaluation feedback. Include current NIST AI RMF/GenAI Profile and August 2026 TEVV-Athlon draft with status clearly labeled. Exclude multi-tool agent trajectory/control evaluation and use of AI to automate conventional QA work.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining AI evaluation theory, experiment architecture, statistical assurance, benchmark and judge validity, risk evidence, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\AI-01.json
```

### AI-02

```text
SUBJECT_ID: AI-02
SUBJECT_TITLE: Agentic-System Testing and Autonomous Quality Engineering
SCOPE DEFINITION: Research evaluation of multi-step LLM/AI agents that plan, use tools, maintain memory, act in environments, and may coordinate with other agents; trajectory and state evaluation; environment simulation; tool authorization, least privilege, side-effect safety, sandboxing, reversibility, stop/hand-off controls, adversarial instructions, memory contamination, long-horizon robustness, recovery, benchmark realism, and cost/latency. Also research AI-assisted generation of conventional tests, models, oracles, repairs, and autonomous QA loops, including validation controls for generated artifacts. Exclude general single-model/LLM benchmark theory except where needed to contrast agent trajectories.
STRUCTURAL OBJECTIVE: Produce a self-contained module explaining agent evaluation theory, harness and simulation architecture, trajectory/side-effect oracles, autonomous-QA control limits, failure modes, and 2026 enterprise implementation.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\AI-02.json
```

### GOV-01

```text
SUBJECT_ID: GOV-01
SUBJECT_TITLE: Risk, Defects, Quality Metrics, Reliability Measures, and Cost of Quality
SCOPE: Research product/project risk quantification and decision theory; defect taxonomies, severity/priority, origin and escape classification; defect density, yield, DRE, escaped-defect, reliability, MTTD/MTTR, change-failure and restoration measures; measurement theory, Goodhart effects, statistical process control, control charts, confidence/uncertainty, and causal limits; prevention/appraisal/internal-failure/external-failure Cost of Quality and decision-economic models. Exclude detailed test methods, TDM/privacy compliance, and organizational/team topology.
STRUCTURAL_OBJECTIVE: Produce a self-contained module explaining defensible metric semantics and formulas, economic decision models, measurement governance, anti-gaming controls, failure modes, and 2026 enterprise implementation.
NEUTRAL_FRAMING: Characterize mechanisms, evidence, limitations, uncertainty, and trade-offs without assuming any metric, economic model, organizational target, tool, or conclusion.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\GOV-01.json
```

### GOV-02

```text
SUBJECT_ID: GOV-02
SUBJECT_TITLE: Test-Data Management, Privacy, Regulation, and Audit Evidence
SCOPE: Research governed test-data provisioning, subsetting, generation, masking, tokenization, and synthetic data; representativeness and referential integrity; access control, retention, lineage, environment separation, and third-party data; privacy principles and privacy risk; risk-based regulated validation and audit traceability across applicable software contexts; immutable or tamper-evident evidence and reproducibility. Exclude product-data correctness algorithms (NFR-05), detailed organizational leadership, and legal advice.
STRUCTURAL_OBJECTIVE: Produce a self-contained module explaining governance architecture, control selection, privacy-safe and statistically useful test data, regulatory/audit evidence design, applicability limits, failure modes, and 2026 enterprise implementation.
NEUTRAL_FRAMING: Characterize mechanisms, evidence, limitations, uncertainty, and trade-offs without assuming any tool, vendor, development method, regulatory regime, or conclusion.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\GOV-02.json
```

### GOV-03

```text
SUBJECT_ID: GOV-03
SUBJECT_TITLE: QA Operating Model, Leadership, Capability Maturity, and Workforce
SCOPE: Research enterprise quality-engineering operating models; centralized, embedded, federated, platform, and community structures; product-team ownership and independent challenge; RACI/decision rights; quality strategy, portfolio risk, assurance planning, and executive governance; capability and maturity assessment; competency models, career paths, education, communities of practice, succession, and ethical professional conduct; vendor, supplier, outsourcing, and managed-service governance; organizational change and adoption. Exclude metric definitions and Cost of Quality calculations (GOV-01), regulatory/test-data controls (GOV-02), and detailed test techniques.
STRUCTURAL_OBJECTIVE: Produce a self-contained module explaining organizational design choices and contingencies, decision/accountability architecture, leadership mechanisms, capability maturity, workforce systems, supplier governance, failure modes, and 2026 enterprise implementation.
NEUTRAL_FRAMING: Characterize mechanisms, evidence, limitations, uncertainty, and trade-offs without assuming any organization chart, sourcing strategy, development method, tool, or conclusion.
OUTPUT_PATH: D:\Documents\GitRoot\aegolius-labs\agentic-qa-kit\research\GOV-03.json
```
