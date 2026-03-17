# Testing gpui_service

## Running Tests

### Using pytest (recommended)
```bash
cd gpui_service
python -m pytest
```

### Using unittest
```bash
cd gpui_service
python -m unittest discover -v
```

### Running specific tests
```bash
python -m pytest test_gptworker_integration.py -v
```

### Test dependencies
- python3
- pytest (optional, for richer output)
- samba (for integration tests)
- dbus-python
- gi (GObject Introspection)

Integration tests requiring Samba will be skipped if Samba is not available.