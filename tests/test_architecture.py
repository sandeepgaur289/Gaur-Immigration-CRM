from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_frozen_legacy_exists():
    assert (ROOT/"legacy_core.py").exists()

def test_modular_registry_exists():
    assert (ROOT/"modules"/"registry.py").exists()

def test_entrypoint_is_thin():
    text=(ROOT/"app.py").read_text(encoding="utf-8")
    assert "from legacy_core import app" in text
    assert "register_modules(app)" in text
    assert len(text) < 2000

def test_required_module_boundaries_exist():
    for name in ["dashboard","leads","enrollments","accounts","reporting","chat","profiles","filing","system"]:
        assert (ROOT/"modules"/name).is_dir()
