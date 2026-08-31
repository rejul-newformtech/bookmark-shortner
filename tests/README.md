# Test Suite Documentation

This directory contains comprehensive test cases for the Link Shortener API.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
  - Database setup and teardown
  - Test client initialization
  - Authentication fixtures
  - Database session management

- **`test_auth.py`** - Authentication endpoint tests
  - User registration tests
  - Login functionality tests
  - Password validation tests
  - Duplicate user handling

- **`test_bookmarks.py`** - Bookmark management tests
  - Bookmark creation tests
  - Bookmark retrieval tests
  - Bookmark deletion tests
  - Authorization checks

- **`test_users.py`** - User profile tests
  - User profile retrieval
  - Profile updates
  - User status management
  - User deletion

- **`test_schemas.py`** - Schema validation tests
  - User schema validation
  - Bookmark schema validation
  - Email validation
  - Password requirement validation

- **`test_utils.py`** - Utility function tests
  - Password hashing and verification
  - Short code generation
  - String manipulation utilities

- **`test_crud.py`** - Database CRUD operation tests
  - User creation and retrieval
  - Bookmark CRUD operations
  - Duplicate handling

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestUserRegistration
```

### Run Specific Test Function
```bash
pytest tests/test_auth.py::TestUserRegistration::test_register_user_success
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Only Failed Tests
```bash
pytest tests/ --lf
```

### Run Tests in Parallel (faster)
```bash
pytest tests/ -n auto
```

## Test Coverage

The test suite covers:

- ✅ Authentication (registration, login, token generation)
- ✅ User management (profile, updates, deletion)
- ✅ Bookmark operations (create, read, delete)
- ✅ Data validation (schemas, email format, password strength)
- ✅ Database operations (CRUD, transactions)
- ✅ Authorization and access control
- ✅ Error handling and edge cases
- ✅ Utility functions (password hashing, short code generation)

## Fixtures

### Database Fixtures
- `db_engine` - SQLite in-memory test database
- `db_session` - SQLAlchemy async session for database operations

### Client Fixtures
- `client` - AsyncClient for making HTTP requests
- `client_with_auth` - Pre-authenticated client

### User Fixtures
- `test_user_data` - Sample user data
- `test_user_data_2` - Second sample user data
- `registered_user` - Pre-registered test user
- `auth_token` - JWT authentication token

## Test Database

Tests use an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) which:
- Is created fresh for each test session
- Provides fast test execution
- Is automatically cleaned up after tests
- Doesn't require Docker or external services

## Dependencies

Make sure to install test dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

Or use the dev dependency group:
```bash
uv sync --group dev
```

## Best Practices

1. Each test should be independent and not rely on other tests
2. Use descriptive test names that explain what is being tested
3. Use fixtures to set up test data
4. Test both success and failure cases
5. Verify error messages in exception tests
6. Keep tests focused on a single behavior

## Debugging Tests

### Run with Debug Output
```bash
pytest tests/ -s
```

### Run with PDB (Python Debugger)
```bash
pytest tests/ --pdb
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

## CI/CD Integration

To run tests in a CI/CD pipeline:

```bash
pytest tests/ \
  --cov=app \
  --cov-report=xml \
  --junitxml=junit.xml \
  --tb=short
```

This generates:
- `junit.xml` - JUnit format for CI/CD systems
- Coverage XML report for coverage tracking
