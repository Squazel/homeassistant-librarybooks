# Testing Guide

This directory contains tests for the Library Books integration. There are two types of tests:

1. **Unit Tests** - Test individual components without external dependencies
2. **Integration Tests** - Test the actual scraper against real library websites

## Setup

### 1. Install Test Dependencies

From the project root directory:

```bash
pip install -r tests/requirements.txt
```

### 2. Set Environment Variables (for integration tests)

Create environment variables for your library credentials:

#### Windows (Command Prompt)
```cmd
set LIBRARY_URL=https://your-library-website.com
set LIBRARY_USERNAME=your_library_username
set LIBRARY_PASSWORD=your_library_password
```

#### Windows (PowerShell)
```powershell
$env:LIBRARY_URL="https://your-library-website.com"
$env:LIBRARY_USERNAME="your_library_username"
$env:LIBRARY_PASSWORD="your_library_password"
```

#### Linux/Mac
```bash
export LIBRARY_URL="https://your-library-website.com"
export LIBRARY_USERNAME="your_library_username"
export LIBRARY_PASSWORD="your_library_password"
```

### 3. Alternative: Create .env file (Optional)

Create a `.env` file in the project root:

```env
LIBRARY_URL=https://your-library-website.com
LIBRARY_USERNAME=your_library_username
LIBRARY_PASSWORD=your_library_password
```

**Note:** Ensure that `.env` has been added to your `.gitignore` to avoid committing credentials!

## Running Tests

### Unit Tests Only

Run the fast unit tests without needing library credentials:

```bash
# From project root
python -m pytest tests/test_models.py -v
```

### All Tests (including integration)

Run all tests including the live library scraper test:

```bash
# From project root
python -m pytest tests/ -v
```

### Specific Test Files

```bash
# Test just the models
python -m pytest tests/test_models.py -v

# Test just the scraper (requires credentials)
python tests/test_libero_scraper.py
```

### Manual Scraper Testing

Test your scraper implementation directly:

```bash
# Set environment variables first, then either:
python tests/test_libero_scraper.py

# Or run via pytest:
python -m pytest tests/test_libero_scraper.py -v -s
```

## Test Structure

```
tests/
├── README.md              # This file
├── requirements.txt       # Test dependencies  
├── conftest.py           # Pytest fixtures and configuration
├── test_models.py        # Unit tests for data models
└── test_libero_scraper.py # Integration test for Libero scraper
```

## Writing New Tests

### Unit Tests

Add new unit tests to existing files or create new `test_*.py` files:

```python
def test_my_function():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == "expected"
```

### Integration Tests

For new library scrapers, copy `test_libero_scraper.py` and modify:

```python
from custom_components.library_books.scrapers.new_scraper import NewLibraryScraper

async def test_new_scraper():
    # Your test implementation
    pass
```

## Fixtures Available

From `conftest.py`:

- `mock_session` - Mocked requests session for unit tests
- `sample_library_book` - Pre-configured LibraryBook object for testing

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:

```bash
python -m pytest tests/
```

### Missing Credentials

If `test_libero_scraper.py` shows the environment variable warning, make sure:

1. Environment variables are set correctly
2. Variable names match exactly (case-sensitive)
3. You're running from the same terminal where you set the variables

### HTTP Request Issues

If the scraper can't connect to your library:

1. Verify the library URL is correct and accessible
2. Check your network connection
3. Ensure the library website is not blocking requests
4. Verify your credentials are correct

### HTML Parsing Issues

If the scraper can't find books, you may need to:

1. Inspect your library's HTML structure
2. Update the parsing logic in `libero_scraper.py`
3. Check the login process and API endpoints
4. Look at the JSON response structure

## Security Notes

- **Never commit credentials** to version control
- Use environment variables or `.env` files for sensitive data
- Add `.env` to your `.gitignore` file
- Consider using test/dummy accounts if available

## Getting Help

If tests fail:

1. Check the error messages carefully
2. Verify your library website is accessible
3. Ensure your credentials are correct
4. Look at the API response to debug parsing issues
5. Check the [main README](../README.md) for additional setup information