# Examples

Runnable Python scripts demonstrating Aletheia's core flows. Each can be run
standalone without installing the package:

```bash
python examples/01_decomposition.py
python examples/02_socratic.py
python examples/03_full_reflection.py
python examples/04_wisdom_graph.py
python examples/05_safety.py
```

All examples use the `MockProvider` by default, so they work offline.

| Example | What it demonstrates |
|---------|----------------------|
| `01_decomposition.py` | Epistemic decomposition: OBSERVATION → INTERPRETATION → ... → ACTION |
| `02_socratic.py` | Socratic question generation with reflection-layer targeting |
| `03_full_reflection.py` | End-to-end reflection: decomposition + 5 layers + questions + wisdom + safety |
| `04_wisdom_graph.py` | Wisdom Graph exploration, disagreement preservation, retrieval |
| `05_safety.py` | Safety Constitution: forbidden-claim detection, anti-dependency breaks |

To use a real LLM provider instead of the mock:

```bash
export ALETHEIA_LLM_PROVIDER=ollama
export ALETHEIA_OLLAMA_MODEL=llama3.1:8b-instruct-q5_K_M
python examples/03_full_reflection.py
```
