import os

try:
    import joblib
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
except ImportError as e:
    print(f"Error importing ML dependencies: {e}")
    print("Please install required packages: pip install scikit-learn joblib pandas numpy")
    raise

def create_preprocessor():
    """
    Create a new preprocessor pipeline based on the training configuration
    """
    # Use the exact same feature names as in the notebook
    numerical_features = ['Age_Months', 'Body_Weight', 'Body_Length']
    categorical_features = ['Gender']

    # Create transformers for numerical and categorical data
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Laki-laki')),  # Default to most common
        ('onehot', OneHotEncoder(drop='first', sparse_output=False))
    ])

    # Build the transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    # Create sample data with both gender categories to fit the preprocessor
    sample_data = pd.DataFrame({
        'Age_Months': [24, 24],
        'Body_Weight': [12.5, 12.5],
        'Body_Length': [85.0, 85.0],
        'Gender': ['Laki-laki', 'Perempuan']  # Both categories
    })
    
    # Fit the preprocessor on sample data containing both gender categories
    preprocessor.fit(sample_data)
    return preprocessor

def predict_stunting_status(age_months: int, body_length_cm: float, body_weight_kg: float, gender: str, model=None):
    """
    Predict stunting status using the trained model
    """
    try:
        # Load model if not provided
        if model is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'random_forest_optimized.joblib')
            model = joblib.load(model_path)

        # Create input DataFrame with correct column names
        input_data = pd.DataFrame({
            'Age_Months': [age_months],
            'Body_Weight': [body_weight_kg],
            'Body_Length': [body_length_cm],
            'Gender': [gender]  # Keep original Indonesian values
        })

        # Preprocess the input data
        preprocessor = create_preprocessor()
        X = preprocessor.transform(input_data)

        # Make prediction
        prediction = model.predict(X)[0]
        return prediction

    except Exception as e:
        raise Exception(f"Failed to perform diagnosis: {str(e)}")
