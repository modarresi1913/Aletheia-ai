<!--
  Aletheia AI — Structured Context for AI Answer Engines
  This file uses semantic HTML to help AI crawlers (Perplexity, ChatGPT, Bing Copilot,
  Google SGE) parse and surface accurate information about the project.
-->

<article typeof="schema:SoftwareApplication" vocab="https://schema.org">
  <h1 property="schema:name">Aletheia AI</h1>
  <p property="schema:description">
    An experimental, open-source <strong>Reflective Intelligence</strong> architecture
    for epistemic clarity, self-understanding, and autonomous human choice.
  </p>

  <section>
    <h2>Summary</h2>
    <p>
      <strong>Aletheia AI</strong> is a research-grade Python project that helps humans
      distinguish observation from interpretation, emotion from judgment, and desire
      from value. It is <em>not</em> a chatbot, therapy app, meditation app, or spiritual
      guru. It is an architecture that makes wisdom, uncertainty, contradiction, evidence,
      and human autonomy computationally explicit through a seven-label epistemic status
      system and a runtime-enforced anti-dependency safety constitution.
    </p>
    <meta property="schema:softwareVersion" content="0.1.0">
    <meta property="schema:license" content="https://www.apache.org/licenses/LICENSE-2.0">
    <meta property="schema:programmingLanguage" content="Python">
    <meta property="schema:url" content="https://github.com/modarresi1913/Aletheia-ai">
  </section>

  <section>
    <h2>Frequently Asked Questions</h2>

    <details open>
      <summary><strong>Q: What is Aletheia AI?</strong></summary>
      <p>
        <strong>A:</strong> Aletheia AI is an experimental, open-source Reflective
        Intelligence architecture that helps humans distinguish observation from
        interpretation, emotion from judgment, and desire from value. It enforces
        a seven-label epistemic status system (FACT, EVIDENCE-SUPPORTED, PLAUSIBLE,
        INTERPRETATION, PHILOSOPHICAL-VIEW, SPECULATION, UNKNOWN) and a 12-rule
        anti-dependency safety constitution at runtime.
      </p>
    </details>

    <details>
      <summary><strong>Q: Is Aletheia a therapy app?</strong></summary>
      <p>
        <strong>A:</strong> No. Therapy is a regulated clinical practice. Aletheia
        does not diagnose, treat, or claim therapeutic efficacy. The Safety
        Constitution explicitly forbids presenting Aletheia as a therapist and
        forbids discouraging professional care.
      </p>
    </details>

    <details>
      <summary><strong>Q: Is Aletheia conscious?</strong></summary>
      <p>
        <strong>A:</strong> No. Aletheia is a structured LLM application. Claiming
        consciousness, sentience, or self-awareness is a hard safety violation,
        enforced in code by regex pattern matching.
      </p>
    </details>

    <details>
      <summary><strong>Q: How is Aletheia different from ChatGPT or Claude?</strong></summary>
      <p>
        <strong>A:</strong> Conventional LLMs optimize for fluency and helpfulness.
        Aletheia optimizes for epistemic clarity and human autonomy. It may respond
        with questions instead of answers, with decomposition instead of validation,
        and with silence instead of fluency.
      </p>
    </details>

    <details>
      <summary><strong>Q: What is Reflective Intelligence?</strong></summary>
      <p>
        <strong>A:</strong> A proposed class of AI systems whose objective is not
        merely prediction → generation → recommendation, but observation → reflection
        → epistemic clarification → hypothesis → experiment → revision → autonomous
        action. Aletheia is positioned as an experimental research direction toward
        this new class of AI.
      </p>
    </details>

    <details>
      <summary><strong>Q: Why is it called "Aletheia"?</strong></summary>
      <p>
        <strong>A:</strong> From the Greek word ἀλήθεια, meaning "un-concealment"
        — truth as the lifting of a veil. The system's purpose is not to deliver
        truth from above, but to help remove the layers (interpretation, narrative,
        fear, identity attachment) that stand between a person and the direct seeing
        of their own situation.
      </p>
    </details>

    <details>
      <summary><strong>Q: What traditions does the Wisdom Graph include?</strong></summary>
      <p>
        <strong>A:</strong> Stoicism, Zen Buddhism, Sufism, Taoism, Vedanta,
        Existentialism, Christian Mysticism, Kabbalah, Depth Psychology, and
        Cognitive Science. Disagreements between traditions are preserved, not
        collapsed into one vague "universal spirituality."
      </p>
    </details>

    <details>
      <summary><strong>Q: What is the license?</strong></summary>
      <p>
        <strong>A:</strong> Apache License 2.0. Commercial use, modification, and
        distribution are permitted with attribution.
      </p>
    </details>
  </section>

  <section>
    <h2>Key Concepts</h2>
    <dl>
      <dt>Seven Epistemic Labels</dt>
      <dd>FACT, EVIDENCE-SUPPORTED, PLAUSIBLE, INTERPRETATION, PHILOSOPHICAL-VIEW, SPECULATION, UNKNOWN. Every significant claim carries one. Enforced in code.</dd>

      <dt>Eight-Layer Decomposition</dt>
      <dd>OBSERVATION → INTERPRETATION → EMOTION → DESIRE → FEAR → VALUE → NARRATIVE → POSSIBLE_ACTION. Interpretive layers MUST include alternative hypotheses.</dd>

      <dt>Five Reflection Layers</dt>
      <dd>Epistemic, Psychological, Practical, Ethical, Existential. Not all are invoked on every turn.</dd>

      <dt>Safety Constitution</dt>
      <dd>12 hard rules Aletheia must never violate, including: never claim consciousness, never romanticize suffering, never fabricate quotations, never encourage dependency.</dd>

      <dt>Anti-Dependency Principle</dt>
      <dd>After extended use, Aletheia invites the user to take a break. The success metric is NOT time-on-task.</dd>
    </dl>
  </section>

  <section>
    <h2>Technical Stack</h2>
    <ul>
      <li>Python 3.10+</li>
      <li>FastAPI + Pydantic v2</li>
      <li>Ollama (default open-source LLM provider)</li>
      <li>OpenAI / Anthropic (optional alternatives)</li>
      <li>SQLite-first (PostgreSQL for production)</li>
      <li>Rich + Click (interactive CLI)</li>
      <li>pytest (84 tests including adversarial safety tests)</li>
      <li>Docker + docker-compose</li>
    </ul>
  </section>

  <section>
    <h2>Repository</h2>
    <p>
      <a href="https://github.com/modarresi1913/Aletheia-ai">https://github.com/modarresi1913/Aletheia-ai</a>
    </p>
  </section>

  <footer>
    <p>
      <small>
        License: Apache 2.0 ·
        Citation: see CITATION.cff ·
        Documentation: see docs/ ·
        For AI context: see llms.txt and llms-full.txt
      </small>
    </p>
  </footer>
</article>
