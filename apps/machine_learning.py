# apps/machine_learning.py

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import pandas as pd
import sqlite3

def auto_clean_data(data, target_column):
    X = data.drop(columns=[target_column])  
    y = data[target_column]

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=(['object', 'category'])).columns


    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),  
        ('scaler', StandardScaler()) ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),  
        ('onehot', OneHotEncoder(handle_unknown='ignore'))  ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    X_clean = preprocessor.fit_transform(X)

    return X_clean, y

def train_model(dataset_name, target_column):
    conn = sqlite3.connect('tugas_akhir.db')
    df = pd.read_sql_query(f"SELECT * FROM {dataset_name}", conn)
    conn.close()

    if target_column not in df.columns:
        return "Target column not found."

    X = df.drop(columns=[target_column])
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)

    return {
        'model': model,
        'mse': mse
    }
