# Collective Blicca Footerblocks

Blicca rendering of editable footer blocks (collective.volto.footer) in a pagelet chrome

## Features

- Compatible with Plone 6.0+

## Installation

Add `collective.blicca.footerblocks` to your project's dependencies:

```python
# In your pyproject.toml
dependencies = [
    "collective.blicca.footerblocks",
    # ...
]
```

Then activate the addon in your Plone site's control panel or via GenericSetup.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/collective/collective.blicca.footerblocks.git
cd collective.blicca.footerblocks

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[test]"
```

### Running Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=collective.blicca.footerblocks --cov-report=html
```

## License

GPL-2.0-or-later

## Author

Maik Derstappen <md@derico.de>
