"""Execute the full test suite and write machine- and human-readable reports."""

from __future__ import annotations

import csv
import logging
import sys
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
OUTPUT_DIR = PROJECT_ROOT / "output" / "tests"


class RecordingResult(unittest.TextTestResult):
    """Collect per-test statuses and failure reasons for exported summaries."""

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.records.append((test.id(), "Passed", ""))

    def addFailure(self, test: unittest.TestCase, err: tuple[object, object, object]) -> None:
        super().addFailure(test, err)
        self.records.append((test.id(), "Failed", self._exc_info_to_string(err, test).splitlines()[-1]))

    def addError(self, test: unittest.TestCase, err: tuple[object, object, object]) -> None:
        super().addError(test, err)
        self.records.append((test.id(), "Error", self._exc_info_to_string(err, test).splitlines()[-1]))


class RecordingRunner(unittest.TextTestRunner):
    """Test runner that initializes report records on its result instance."""

    resultclass = RecordingResult

    def _makeResult(self) -> RecordingResult:
        result = super()._makeResult()
        result.records = []
        return result


def write_reports(result: RecordingResult, elapsed: float) -> None:
    """Write detailed TXT and single-row CSV test summaries."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = len(result.failures) + len(result.errors)
    passed = result.testsRun - failures
    status = "PASSED" if failures == 0 else "FAILED"
    lines = [
        "==========================================",
        "E-COMMERCE ANALYTICS TEST REPORT",
        "==========================================",
        f"Total Tests: {result.testsRun}",
        f"Passed: {passed}",
        f"Failed: {failures}",
        "Warnings: 0",
        f"Execution Time: {elapsed:.2f} sec",
        f"Project Status: {status}",
        "",
        "Test Details:",
        *[f"{name} | {state}{': ' + reason if reason else ''}" for name, state, reason in result.records],
        "==========================================",
    ]
    (OUTPUT_DIR / "test_report.txt").write_text("\n".join(lines), encoding="utf-8")
    with (OUTPUT_DIR / "test_summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["total_tests", "passed", "failed", "warnings", "execution_seconds", "status"])
        writer.writeheader()
        writer.writerow({"total_tests": result.testsRun, "passed": passed, "failed": failures, "warnings": 0, "execution_seconds": f"{elapsed:.2f}", "status": status})


def main() -> int:
    """Discover, execute, report, and return a process status code."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    suite = unittest.defaultTestLoader.discover(str(TESTS_DIR), pattern="test_*.py", top_level_dir=str(PROJECT_ROOT))
    started = time.perf_counter()
    result = RecordingRunner(verbosity=1).run(suite)
    elapsed = time.perf_counter() - started
    write_reports(result, elapsed)
    print("\n==========================================")
    print("E-COMMERCE ANALYTICS TEST REPORT")
    print("==========================================")
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures) + len(result.errors)}")
    print("Warnings: 0")
    print(f"Execution Time: {elapsed:.2f} sec")
    print(f"Project Status: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    print("==========================================")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
