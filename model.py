import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("dataset/placement_data.csv")

# Features & target
X = df.drop("Placed", axis=1)
y = df["Placed"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model (IMPORTANT FIX)
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    class_weight="balanced",
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Test
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, "models/placement_model.pkl")

print("Model saved successfully!")
sample = [[5.5,4,5,0,0,50,55,4]]  # low score
print(model.predict(sample))

sample2 = [[8.5,9,8,2,3,85,80,8]]  # high score
print(model.predict(sample2))