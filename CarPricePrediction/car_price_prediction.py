# car_price_prediction.py

# Import libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 1. Load dataset
# Make sure car_data.csv is in the same folder
df = pd.read_csv("car_data.csv")

print("First 5 rows of dataset:")
print(df.head())

# 2. Preprocessing
# Derive new feature: Car Age
df["Car_Age"] = 2025 - df["Year"]   # Assuming current year 2025
df.drop("Year", axis=1, inplace=True)

# Drop Car_Name (not useful for prediction)
df.drop("Car_Name", axis=1, inplace=True)

# Encode categorical columns
label_encoder = LabelEncoder()
for col in ["Fuel_Type", "Seller_Type", "Transmission"]:
    df[col] = label_encoder.fit_transform(df[col])

print("\nData after preprocessing:")
print(df.head())

# 3. Split features and target
X = df.drop("Selling_Price", axis=1)
y = df["Selling_Price"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Predictions & Evaluation
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation:")
print(f"RMSE: {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

# 6. Test with a new input
sample_car = {
    "Present_Price": 10,
    "Driven_kms": 30000,
    "Fuel_Type": 1,       # 0 = Diesel, 1 = Petrol
    "Seller_Type": 0,     # 0 = Dealer, 1 = Individual
    "Transmission": 1,    # 0 = Manual, 1 = Automatic
    "Owner": 0,
    "Car_Age": 5
}

sample_df = pd.DataFrame([sample_car])
predicted_price = model.predict(sample_df)[0]
print(f"\nPredicted Selling Price for sample car: {predicted_price:.2f} lakhs")
