# Testing gpui_service

**Requires Python 3.6+** (uses f-strings, pathlib, and other Python 3 features)

## Running Tests

### Using the test runner script (recommended)
```bash
cd gpui_service
python3 run_tests.py
```

For pytest (if installed):
```bash
python3 run_tests.py --pytest
```

### Using unittest directly
```bash
cd gpui_service
python3 -m unittest discover -v
```

### Using pytest directly
```bash
cd gpui_service
python3 -m pytest
```

### Running specific tests
```bash
python3 -m pytest test_gptworker_integration.py -v
```

### Test dependencies
- python3 (3.6+)
- pytest (optional, for richer output)
- samba (for integration tests)
- dbus-python
- gi (GObject Introspection)

Integration tests requiring Samba will be skipped if Samba is not available.

## Troubleshooting

If you get syntax errors:
- Ensure you're using Python 3.6+: `python3 --version`
- On systems where `python` defaults to Python 2.7, explicitly use `python3`
- The test runner script (`run_tests.py`) automatically checks Python version