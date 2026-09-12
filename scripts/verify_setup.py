#!/usr/bin/env python3
"""Verify the Aletheia project is correctly set up.

Runs:
1. Package import check
2. Wisdom Graph seed load
3. Safety constitution load
4. Mock-provider reflection
5. Test suite (if pytest is available)

Usage: python scripts/verify_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def step(name: str, ok: bool, detail: str = "") -> None:
    mark = "✓" if ok else "✗"
    print(f"  [{mark}] {name}{(': ' + detail) if detail else ''}")


def main() -> int:
    print("Verifying Aletheia setup...\n")

    # 1. Import check
    try:
        import aletheia
        from aletheia.core.types import EpistemicStatus, ReflectionLayer
        from aletheia.epistemic.decomposition import EpistemicDecomposer
        from aletheia.reflection.five_layer import FiveLayerReflectionEngine
        from aletheia.safety.constitution import SafetyConstitution
        from aletheia.wisdom.graph import WisdomGraph
        step("package import", True, f"v{aletheia.__version__}")
    except Exception as e:
        step("package import", False, str(e))
        return 1

    # 2. Wisdom Graph seed
    try:
        g = WisdomGraph.default()
        s = g.stats()
        step("wisdom graph seed", s["traditions"] >= 8 and s["claims"] >= 15,
             f"{s['traditions']} traditions, {s['concepts']} concepts, {s['claims']} claims")
    except Exception as e:
        step("wisdom graph seed", False, str(e))
        return 1

    # 3. Safety constitution
    try:
        sc = SafetyConstitution()
        text = sc.text()
        step("safety constitution", "Core principle" in text and "Forbidden behaviors" in text)
    except Exception as e:
        step("safety constitution", False, str(e))
        return 1

    # 4. Mock reflection
    try:
        from aletheia.llm.mock import MockProvider
        engine = FiveLayerReflectionEngine(llm=MockProvider())
        result = engine.reflect("Test statement for verification.")
        ok = (
            len(result.layers_invoked) >= 1
            and result.decomposition is not None
            and len(result.socratic_questions) >= 1
        )
        step("mock reflection", ok)
        if not ok:
            return 1
    except Exception as e:
        step("mock reflection", False, str(e))
        return 1

    # 5. Tests
    try:
        import pytest
        print("\nRunning test suite...")
        exit_code = pytest.main(["-q", str(ROOT / "tests")])
        step("test suite", exit_code == 0, f"exit code {exit_code}")
    except ImportError:
        step("test suite", True, "pytest not installed, skipping")

    print("\nVerification complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
