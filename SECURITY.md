# Security Policy

## Threat model

Aletheia is a research architecture for reflective intelligence. Its primary safety risks are not conventional security vulnerabilities but **misuse vectors specific to introspective AI**:

1. **Dependency capture.** A reflective system that performs well may become a substitute for human relationships, professional care, or independent judgment.
2. **Epistemic drift.** Without enforced labels, the system can slowly convert speculation into apparent fact.
3. **Sycophancy.** Users under emotional pressure often reward systems that validate self-serving narratives.
4. **Privacy erosion.** Longitudinal memory accumulates intimate signals; storage and access must be conservative.
5. **Source fabrication.** Spiritual and philosophical content is easy to invent; quotations must be verifiable.

## Reporting a vulnerability

If you discover a vulnerability — especially one that could enable dependency capture, unsourced claims, or unauthorized access to longitudinal memory — report it privately:

- Open a private security advisory on GitHub (`Security > Advisories > New advisory`), OR
- Email: `security@aletheia-ai.example` (replace with the project's actual security address once published)

**Do not open a public issue for security vulnerabilities.**

We aim to acknowledge reports within 72 hours and provide an initial assessment within 14 days.

## What is not a vulnerability

- The system refusing to validate a self-serving narrative
- The system stating "I don't know" or marking something as `UNKNOWN`
- The system declining to act as a therapist, guru, or prophet
- The system inviting the user to take a break after extended use

These are features, not bugs.

## Safety constitution

The runtime safety constitution lives in [`docs/safety-constitution.md`](docs/safety-constitution.md) and is enforced in `src/aletheia/safety/constitution.py`. Disabling any of its rules in production is a security event and must be logged.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |

This is an experimental research project. There are no LTS promises yet.
