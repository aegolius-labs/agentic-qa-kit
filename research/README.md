# Research Corpus: Modern Quality Engineering (2026)

This directory contains the isolated research deliverables, dispatch record, and source-audit materials used to compile the manual.

## Master taxonomy

The taxonomy partitions the software-quality domain by assurance object and lifecycle control point. A subject owns a concept only when it is the principal place where that concept is specified; later chapters may cross-reference it without redefining it.

| ID | Track | Subject | Inclusion boundary | Principal exclusions |
|---|---|---|---|---|
| FND-01 | Foundations and theory | Quality theory, quality models, testing standards, and evidence | V&V concepts; quality attributes; ISO/IEC 25010; ISO/IEC/IEEE 29119; evidence semantics | Detailed design techniques and execution architectures |
| FND-02 | Foundations and theory | Specification-based test design and behavioral modeling | Partitions, boundaries, decision tables, cause-effect graphs, classification trees, scenarios, state transitions, oracles | Combinatorial, mutation, static, and NFR methods |
| FND-03 | Foundations and theory | Combinatorial, model-based, search-based, mutation, and coverage-adequacy methods | Covering arrays, generation algorithms, mutation, structural adequacy, empirical limits | Basic black-box techniques and program analysis |
| SL-01 | Shift-left architecture | Static program analysis and formal verification | AST/IR inspection, data-flow, abstract interpretation, symbolic/concolic execution, SMT, formal proof | Runtime security scanning and executable API contracts |
| SL-02 | Shift-left architecture | Executable specifications, contract testing, property-based testing, and developer feedback | OpenAPI/schema validation, consumer/provider contracts, generative properties, TDD/IDE/pre-commit feedback | General static analysis and pipeline fleet design |
| CT-01 | Continuous testing | Hermetic continuous-test infrastructure and ephemeral environments | Reproducible builds, isolation, containers, service virtualization, environment orchestration, artifact provenance | Selection, scheduling, flakes, and release experimentation |
| CT-02 | Continuous testing | Test selection, prioritization, parallelism, and suite trust | TIA/regression selection, prioritization, sharding, flake detection, quarantine, retry semantics | Environment construction and NFR execution |
| NFR-01 | Non-functional engineering | Performance, scalability, and capacity assurance | Load/stress/spike/endurance tests, workload models, queuing, SLO-aligned capacity | Fault injection, disaster recovery, and field observability |
| NFR-02 | Non-functional engineering | Reliability, resilience, chaos, and recovery assurance | Fault models, injection, steady-state hypotheses, failover, backup/restore, disaster recovery, reliability growth | Nominal capacity testing and progressive delivery |
| NFR-03 | Non-functional engineering | Security assurance across the SDLC | Threat-informed testing, SAST/DAST/IAST/SCA, fuzzing, penetration evidence, supply-chain security checks | General static correctness and compliance governance |
| NFR-04 | Non-functional engineering | Accessibility, usability, compatibility, and internationalization | WCAG 2.2+, assistive technology, human evaluation, cross-platform and locale behavior | Performance and data correctness |
| NFR-05 | Non-functional engineering | Data quality, integrity, persistence, and migration assurance | Constraints, transactions, concurrency, ETL, lineage behavior, migrations, reconciliation | Test-data provisioning policy, privacy governance, analytics economics |
| SR-01 | Shift-right quality | Observability-driven testing and field diagnosability | OpenTelemetry, logs/metrics/traces, correlation, runtime invariants, test observability | Release control and end-user experimentation |
| SR-02 | Shift-right quality | Progressive delivery, synthetic monitoring, traffic shadowing, and RUM | Canary analysis, feature flags, synthetic probes, shadow traffic, RUM feedback, rollback decisions | Telemetry instrumentation internals and preproduction NFR testing |
| AI-01 | AI-native systems | Evaluation and assurance of ML, LLM, and nondeterministic systems | Statistical evaluation, benchmark design, robustness, safety, fairness, drift, LLM judges and human evaluation | Multi-tool agent control and QA-process automation |
| AI-02 | AI-native systems | Agentic-system testing and autonomous quality engineering | Multi-step agent trajectories, tool safety, simulation, metamorphic oracles, AI-generated tests, autonomous QA controls | General model benchmarking and conventional static analysis |
| GOV-01 | Governance and economics | Risk, defects, quality metrics, reliability measures, and Cost of Quality | Defect taxonomy, DRE, density, escapes, MTTD/MTTR, CoQ, control charts, decision economics | Data/privacy compliance and organizational design |
| GOV-02 | Governance and economics | Test-data management, privacy, regulation, and audit evidence | Synthetic/masked data, environments, retention, access, privacy, regulated validation, traceability, audit packages | Product-data correctness algorithms and staffing models |
| GOV-03 | Governance and economics | QA operating model, leadership, capability maturity, and workforce | Team topology, accountability, strategy, portfolio risk, competency, communities of practice, maturity and vendor governance | Metric definitions and regulatory control details |

## Taxonomy construction evidence

The partition is anchored in the lifecycle/process decomposition of ISO/IEC/IEEE 29119, the nine-characteristic product-quality model of ISO/IEC 25010:2023, and the broader software-engineering knowledge-area framing used by SWEBOK. It is expanded where 2026 practice requires distinct control systems: hermetic CI, change-aware execution, observability, progressive delivery, AI/agent evaluation, and governed production feedback.

## Dispatch protocol

Exactly one isolated GPT-5.6 Luna subagent at X-High inference is assigned to each of the 19 rows. `fork_turns: none` prevents inheritance of the orchestration conversation. Every prompt has the same neutral framing, source hierarchy, verification constraints, JSON schema, and minimum evidence threshold; only the subject identity, scope boundary, structural objective, and output path differ. The complete reconstructable prompt record is maintained in `dispatch-prompts.md`.
