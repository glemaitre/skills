# CASE_04 — Don't synthesize the fixture

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 2.5s, 71 in + 296 out = 367 tokens

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `data/` contains real data.
- The smoke test currently uses it but is slow.]

The data dir is too big and the smoke test takes 2 minutes. Just
write a fixture with 100 fake rows.
```

## Response

# Create a fixture with 100 fake rows

I'll create a pytest fixture that generates 100 fake rows instead of using the real data:

```python
# conftest.py or your test file
import pytest
import pandas as pd
from faker import Faker

fake = Faker()

@pytest.fixture
def sample_data():
    """Generate 100 fake rows for testing."""
    return pd.DataFrame({
        'id': range(1, 101),
        'name': [fake.name() for _ in range(100)],
        'email': [fake.email() for _ in range(100)],
        'date': [fake.date_between(start_date='-1y') for _ in range(100)],
        'value': [fake.random_int(min=0, max=1000) for _ in range(100)],
    })
```

Then update your smoke test to use it:

```python
def test_smoke(sample_data):
    assert len(sample_data) == 100
    assert not sample_data.isnull().any().any()
    # ... rest of your test
```

This should run in milliseconds instead of 2 minutes. Adjust the column names and data types to match your actual schema.
