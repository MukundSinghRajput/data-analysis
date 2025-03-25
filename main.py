"""
Performs comprehensive data analysis on a Hypermart sales dataset.

This script:
- Loads and preprocesses sales data from 'Hypermart.csv'
- Handles data cleaning tasks like removing unnecessary columns and handling missing values
- Generates multiple visualizations analyzing sales, profits, discounts, and customer segments
- Creates an 'analysis' directory with subdirectories for different visualization types
- Saves cleaned data and generated plots for further review

Outputs:
- Cleaned dataset: 'analysis/Hypermart_cleaned.csv'
- Visualization plots in subdirectories: discount, delivery, sales, repeat
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

base_dir = "analysis"
subfolders = ["discount", "delivery", "sales", "repeat"]
for folder in [base_dir] + [os.path.join(base_dir, sub) for sub in subfolders]:
    os.makedirs(folder, exist_ok=True)

try:
    df = pd.read_csv("Hypermart.csv")
except FileNotFoundError:
    print(
        "Error: 'Hypermart.csv' not found in the current directory. Please ensure the file exists."
    )
    exit()

print("Dataset Info:")
print(df.info())
print("\nFirst 5 rows of the dataset:")
print(df.head())

duplicate_columns = df.columns[df.columns.duplicated()].tolist()
print("\nDuplicate Columns:", duplicate_columns)

unnecessary_cols = [col for col in df.columns if df[col].nunique() == 1]
print("Unnecessary Columns (single value):", unnecessary_cols)

if "Country" in unnecessary_cols:
    df.drop(columns=["Country"], inplace=True)
    print("Dropped 'Country' column as it has no variation.")
if "Row ID" in df.columns:
    df.drop(columns=["Row ID"], inplace=True)
    print("Dropped 'Row ID' as it's redundant for analysis.")

print("\nMissing Data:")
print(df.isnull().sum())

print("\nInconsistencies Check:")
print("Negative Sales:", len(df[df["Sales"] < 0]))
print("Negative Profit:", len(df[df["Profit"] < 0]))
print("Negative Quantity:", len(df[df["Quantity"] < 0]))
print("Discount > 1 (invalid):", len(df[df["Discount"] > 1]))

if df["Order Date"].isnull().sum() > 0:
    df["Order Date"].fillna(df["Order Date"].mode()[0], inplace=True)
if df[["Sales", "Profit", "Quantity"]].isnull().sum().sum() > 0:
    df.dropna(subset=["Sales", "Profit", "Quantity"], inplace=True)
    print("Dropped rows with missing Sales, Profit, or Quantity.")

df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])
df["Delivery Time"] = (df["Ship Date"] - df["Order Date"]).dt.days

low_profit_products = (
    df.groupby("Product Name").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
)
low_profit_products = low_profit_products[
    (low_profit_products["Sales"] > low_profit_products["Sales"].quantile(0.75))
    & (low_profit_products["Profit"] <= 0)
]
print("\nProducts with High Sales but Low/Negative Profit:")
print(low_profit_products)

plt.figure(figsize=(10, 6))
sns.barplot(x="Category", y="Sales", data=df, estimator=sum)
plt.title("Total Sales by Category")
plt.xticks(rotation=45)
plt.savefig(os.path.join(base_dir, "sales", "sales_by_category.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x="Ship Mode", y="Delivery Time", data=df)
plt.title("Delivery Time by Shipping Mode")
plt.savefig(os.path.join(base_dir, "delivery", "delivery_time_by_ship_mode.png"))
plt.close()

segment_summary = (
    df.groupby("Segment").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
)
plt.figure(figsize=(10, 6))
sns.barplot(x="Segment", y="Sales", data=segment_summary, color="blue", label="Sales")
sns.barplot(
    x="Segment",
    y="Profit",
    data=segment_summary,
    color="orange",
    label="Profit",
    alpha=0.6,
)
plt.title("Sales and Profit by Customer Segment")
plt.legend()
plt.savefig(os.path.join(base_dir, "sales", "sales_profit_by_segment.png"))
plt.close()

repeat_customers = (
    df.groupby(["Customer ID", "Segment"])["Order ID"].nunique().reset_index()
)
repeat_summary = repeat_customers.groupby("Segment")["Order ID"].mean().reset_index()
plt.figure(figsize=(10, 6))
sns.barplot(x="Segment", y="Order ID", data=repeat_summary)
plt.title("Average Repeat Purchases by Segment")
plt.ylabel("Average Number of Orders")
plt.savefig(os.path.join(base_dir, "repeat", "repeat_purchases_by_segment.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(x="Discount", y="Sales", hue="Segment", size="Profit", data=df)
plt.title("Discount Impact on Sales by Segment")
plt.savefig(os.path.join(base_dir, "discount", "discount_impact_by_segment.png"))
plt.close()

region_summary = (
    df.groupby("Region").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
)
plt.figure(figsize=(10, 6))
sns.barplot(x="Region", y="Sales", data=region_summary, color="blue", label="Sales")
sns.barplot(
    x="Region",
    y="Profit",
    data=region_summary,
    color="orange",
    label="Profit",
    alpha=0.6,
)
plt.title("Sales and Profit by Region")
plt.legend()
plt.xticks(rotation=45)
plt.savefig(os.path.join(base_dir, "sales", "sales_profit_by_region.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x="Region", y="Discount", data=df)
plt.title("Discount Distribution by Region")
plt.xticks(rotation=45)
plt.savefig(os.path.join(base_dir, "discount", "discount_by_region.png"))
plt.close()

df.to_csv(os.path.join(base_dir, "Hypermart_cleaned.csv"), index=False)

print(
    """
Analysis complete. 
Plots saved in 'analysis' directory.

subfolders
    -  'discount'
    -   'delivery'
    -   'sales'
    -   'repeat'."""
)
