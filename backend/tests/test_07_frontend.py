"""Section H: Frontend build & smoke tests.

Checks that npm build and dev server start without errors.
Browser automation is not available in this environment, so the
interactive UI verification is documented as a manual checklist.
"""

import os
import subprocess
import sys
import time

BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")


MANUAL_CHECKLIST = """
### Manual UI checklist (run by a human with a browser)

Open http://localhost:5173 in a browser before checking items below.

- [ ] All 5 cases appear in the selector
- [ ] case_pass shows no red-bordered box
- [ ] case_bad_search shows only the Search box red-bordered
- [ ] case_bad_tool shows only the Tool box red-bordered
- [ ] case_bad_generation shows only the Answer box red-bordered
- [ ] case_ambiguous shows BOTH Search and Tool red-bordered
- [ ] Clicking a red-bordered box shows a non-empty explanation
- [ ] Clicking a non-red box shows raw input/output only, no explanation text
- [ ] "Recompute live" shows a loading state, then updates the timeline
- [ ] With an invalid key, "Recompute live" shows the fallback note
      ("using cached result") instead of crashing
"""


def test_npm_build_completes():
    """npm run build must exit with code 0."""
    result = subprocess.run(
        ["npm.cmd", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, (
        f"npm run build failed (code {result.returncode}):\n{result.stderr}"
    )


def test_npm_dev_starts():
    """npm run dev must start and serve on the expected port (5173)."""
    proc = subprocess.Popen(
        ["npm.cmd", "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        start = time.time()
        ready = False
        output_lines = []
        while time.time() - start < 20:
            line = proc.stdout.readline() if proc.stdout else ""
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.2)
                continue
            output_lines.append(line)
            if "localhost" in line.lower() or "ready" in line.lower() or "5173" in line:
                ready = True
                break

        assert ready, (
            f"npm run dev did not become ready within 20s.\n"
            f"Output captured:\n{''.join(output_lines[-20:])}"
        )
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_manual_checklist_printed():
    """Print the manual UI checklist — this test always passes (informational)."""
    print(MANUAL_CHECKLIST)
    assert True
