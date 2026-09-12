# Contributing to Aletheia AI

> *"Aletheia should not become the authority inside a person's mind. It should become a better instrument through which the person can examine their own mind."*

Thank you for considering a contribution. Aletheia is an experimental research project with strong epistemic commitments. Contributions that preserve those commitments are welcome; contributions that erode them will be declined, even if technically excellent.

## 1. Project philosophy

Before contributing, read [`docs/philosophy.md`](docs/philosophy.md) and [`docs/safety-constitution.md`](docs/safety-constitution.md). Two principles are non-negotiable:

1. **Epistemic honesty over fluency.** Never add features that present speculation as fact, blur observation and interpretation, or fabricate sources.
2. **Human autonomy over engagement.** Never optimize for time-on-task, emotional dependency, or persuasion.

If a proposed feature is incompatible with either principle, it does not belong in this repository, regardless of demand.

## 2. What we accept

- Implementations of existing architecture modules described in `docs/architecture.md`
- New seed data for the Wisdom Graph, provided it follows the schema in `docs/wisdom-graph.md` and includes proper sources
- Evaluation cases for the Reflective Intelligence Benchmark (see `docs/evaluation.md`)
- Bug fixes, performance improvements, and better tests
- Documentation improvements
- New LLM provider adapters, kept under the `LLMProvider` interface

## 3. What we will refuse

- Anything that frames Aletheia as a guru, therapist, prophet, or spiritual authority
- Anything that encourages dependency, isolation, or replacement of human relationships
- Anything that romanticizes suffering or uses mortality to manipulate
- Anything that drops the epistemic status labels (`FACT`, `INTERPRETATION`, `SPECULATION`, etc.)
- Fabricated quotations or unsourced wisdom claims
- Anything that converts philosophical speculation into factual certainty

## 4. Development setup

```bash
git clone https://github.com/aletheia-ai/aletheia-ai.git
cd aletheia-ai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,ollama]"
cp .env.example .env
pytest
```

## 5. Pull request checklist

- [ ] Tests added or updated
- [ ] `pytest` passes locally
- [ ] `ruff check src tests` passes
- [ ] `mypy src/aletheia` passes
- [ ] No secrets, API keys, or personal data committed
- [ ] Documentation updated if behavior changed
- [ ] If touching `safety/` or `epistemic/`, an explicit note on why the change preserves the safety constitution

## 6. Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(epistemic): add probabilistic confidence to decomposition
fix(socratic): avoid leading questions in fear-context
docs(safety): clarify anti-dependency enforcement
test(wisdom): add seed-data integrity check
```

## 7. Licensing

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## 8. Code of conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Be rigorous, be kind, and assume good faith in reviewers.
