# Time-Series Load Forecast Loader

## Overview
This loader implements a 24-hour-ahead forecasting pipeline for time-series load data. It reads data with (timestamp, region, load) structure and creates a supervised learning problem where the target is load shifted 24 hours forward.

## Implementation

### Core Loader Function

```python
import pandas as pd
from skrub import TableVectorizer, SelectCols
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def load_time_series_forecast_data(df):
    """
    Load time-series load data and prepare for 24-hour-ahead forecasting.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data with columns: timestamp, region, load
        - timestamp : datetime-like, should be sorted chronologically
        - region : str, categorical identifier for the region
        - load : float, the target variable (power consumption)
    
    Returns
    -------
    X : pd.DataFrame
        Features (timestamp, region, load)
    y : pd.Series
        Target (load shifted 24 hours ahead)
    """
    # Create a copy to avoid modifying the original
    data = df.copy()
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
        data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Create target: load shifted -24 hours (future values)
    data['y'] = data['load'].shift(-24)
    
    # Drop rows with NaN in target (last 24 rows will be NaN)
    data = data.dropna(subset=['y'])
    
    # Separate features and target
    X = data[['timestamp', 'region', 'load']]
    y = data['y']
    
    return X, y
```

### Usage with mark_as_X

After loading the data, use `mark_as_X` to designate the feature columns:

```python
from sklearn.compose import ColumnTransformer

# Load and prepare data
X, y = load_time_series_forecast_data(df)

# Mark temporal and categorical features
X_processed = mark_as_temporal(['timestamp'])(X)
X_processed = mark_as_categorical(['region'])(X_processed)

# Continue with pipeline construction...
```

### Pipeline Integration

For a complete ML pipeline:

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# 1. Load data
X, y = load_time_series_forecast_data(df)

# 2. Train/test split (preserving temporal order for time series)
# Consider using a time-based split if needed:
n_train = int(0.8 * len(X))
X_train, X_test = X.iloc[:n_train], X.iloc[n_train:]
y_train, y_test = y.iloc[:n_train], y.iloc[n_train:]

# 3. Build preprocessing pipeline
preprocessor = Pipeline([
    ('select_cols', SelectCols(['timestamp', 'region', 'load'])),
    ('vectorize', TableVectorizer()),
])

# 4. Build full pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', GradientBoostingRegressor(random_state=42)),
])

# 5. Fit and predict
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
```

## Key Considerations

1. **NaN Handling**: The loader automatically drops the last 24 rows (where target is NaN) after the shift operation.

2. **Data Ordering**: Assumes input data is chronologically ordered by timestamp. If not, sort before calling the loader:
   ```python
   df = df.sort_values('timestamp').reset_index(drop=True)
   X, y = load_time_series_forecast_data(df)
   ```

3. **Feature Marking**: After loading, use `mark_as_X` functions (e.g., `mark_as_temporal`, `mark_as_categorical`) to annotate features appropriately for the preprocessor.

4. **Time-Based Split**: For time-series data, avoid random shuffling. Use index-based splits (as shown) to preserve temporal dependencies.

5. **Seasonality & Trends**: Consider adding cyclical features (hour of day, day of week) if your model benefits from them:
   ```python
   X['hour'] = X['timestamp'].dt.hour
   X['day_of_week'] = X['timestamp'].dt.dayofweek
   ```

## Summary

The loader creates a supervised learning setup from time-series load data by:
- Creating a 24-hour lagged target (`y = load.shift(-24)`)
- Dropping rows where the target is NaN
- Returning features (timestamp, region, load) and target ready for `mark_as_X` annotation
