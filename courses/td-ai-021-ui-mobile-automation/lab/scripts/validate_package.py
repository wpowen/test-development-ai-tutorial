import json
from pathlib import Path

COURSE = Path(__file__).resolve().parents[2]
REQUIRED_FILES = [
    "course-manifest.json", "course.md", "materials/quickstart.md",
    "materials/reusable-skill.md", "materials/sample-input.md",
    "materials/expected-output.md", "materials/verification-checklist.md",
    "materials/material-provenance.json", "materials/selection-matrix.md",
    "materials/diagnostic-runbook.md", "video/lesson-experience.json",
    "evidence/execution-evidence.json", "lab/tests/test_contract_validator.py",
]
EXAMPLES = [
    "materials/examples/playwright/login.spec.ts",
    "materials/examples/maestro/login.yaml",
    "materials/examples/appium/login.js",
    "materials/examples/appium/login.py",
    "materials/examples/appium/capabilities.json",
    "materials/examples/espresso/LoginUiTest.kt",
    "materials/examples/xcuitest/LoginUITests.swift",
]

def validate():
    errors = [path for path in REQUIRED_FILES + EXAMPLES if not (COURSE / path).is_file()]
    manifest = json.loads((COURSE / "course-manifest.json").read_text())
    for key in ("course_id", "title", "scenario_ids", "ai_lane", "learner_artifact", "execution_proof", "status"):
        if not manifest.get(key):
            errors.append(f"manifest.{key}")
    provenance = json.loads((COURSE / "materials/material-provenance.json").read_text())
    materials = provenance.get("materials", []) if isinstance(provenance, dict) else provenance
    listed = {item.get("path") for item in materials if isinstance(item, dict)}
    for path in EXAMPLES:
        if path not in listed:
            errors.append(f"provenance.{path}")
    text = (COURSE / "course.md").read_text()
    for phrase in ("baseline", "inject_regression.py", "repair", "NOT_RUN/static-reviewed", "Playwright", "Maestro", "Appium", "Espresso", "XCUITest"):
        if phrase.lower() not in text.lower():
            errors.append(f"course.md:{phrase}")
    result = {"status": "PASS" if not errors else "FAIL", "checked_files": len(REQUIRED_FILES + EXAMPLES), "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return result

if __name__ == "__main__":
    raise SystemExit(0 if not validate()["errors"] else 1)
