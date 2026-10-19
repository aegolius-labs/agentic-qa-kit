# Security policy

## Supported versions

Security fixes are provided for the latest released minor version. Before
`1.0.0`, support is best effort and may require upgrading to the newest release.

## Reporting a vulnerability

Use GitHub private vulnerability reporting for the
`aegolius-labs/agentic-qa-kit` repository. If private reporting is unavailable,
contact Aegolius Labs through the organization page at
https://github.com/aegolius-labs and request a private reporting channel.

Do not disclose a suspected vulnerability in a public issue. Include the
affected version, reproduction steps, impact, and any suggested mitigation.
Never include credentials, production data, personal information, or private QA
evidence.

## Security boundaries

The kit is a set of agent skills and a local, dependency-free evidence ledger.
The ledger writes only below the target's `.agentic-qa/` directory and never
executes tests, contacts a network service, or authorizes an effect. The host
agent runs checks with the target repository's own permissions.

The skills treat these as separate point-of-action boundaries that a broad
request such as "full QA" does not cross: dependency installation, destructive
or load tests, production access, sensitive or customer data, external
messages, and material cost. A host permission mode, a saved command approval,
or an approval given in another task is not authority for the current action.
A skill that crosses one of these boundaries without explicit authorization is
a security defect; report it as one.

Backlog handoff emits a payload only. Ingestion and GitHub synchronization
belong to Agentic Backlog Kit and its plan, digest, and confirmation contract.

Session evidence can capture environment details, command output, and file
paths. Generated evidence is ignored by version control by default; review it
before sharing.
