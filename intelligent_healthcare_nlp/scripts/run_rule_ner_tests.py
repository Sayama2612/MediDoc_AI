"""Simple test runner for rule_ner tests (works without pytest).
This will import the test functions and run them, reporting failures.
"""
import importlib
import traceback
import os
import sys

# ensure project root (intelligent_healthcare_nlp) is on sys.path so tests can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

mod = importlib.import_module('tests.test_rule_ner')

tests = [
    'test_happy_path_extraction',
    'test_admission_and_discharge_mapping',
    'test_multiple_medication_parsing',
    'test_no_medication',
]

failed = 0
for t in tests:
    fn = getattr(mod, t, None)
    if not fn:
        print(f'MISSING: {t}')
        failed += 1
        continue
    try:
        fn()
        print(f'PASS: {t}')
    except AssertionError as e:
        failed += 1
        print(f'FAIL: {t} - AssertionError: {e}')
        traceback.print_exc()
    except Exception as e:
        failed += 1
        print(f'ERROR: {t} - Exception: {e}')
        traceback.print_exc()

if failed:
    print(f"{failed} test(s) failed")
    raise SystemExit(1)
else:
    print('All rule_ner tests passed')
