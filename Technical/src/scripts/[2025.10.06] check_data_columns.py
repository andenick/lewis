import os
import pandas as pd
from pathlib import Path
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BOP_PATH = DATA_ROOT / "BALANCE_OF_PAYMENTS"
GDP_PATH = DATA_ROOT / "GDP"

print("US columns:")
us = pd.read_excel(BOP_PATH / "US_BEA" / "BoP_USRData_NA.xlsx")
for i, col in enumerate(us.columns):
    print(f"  {i}: {col}")

print("\nUK columns:")
uk = pd.read_excel(BOP_PATH / "UK_ONS" / "BoP_UKRData_NA.xlsx")
for i, col in enumerate(uk.columns):
    print(f"  {i}: {col}")

print("\nGermany columns:")
ger = pd.read_excel(BOP_PATH / "Germany_Bundesbank" / "BoP_GermanyRData_NA.xlsx")
for i, col in enumerate(ger.columns):
    print(f"  {i}: {col}")

print("\nGDP columns:")
gdp = pd.read_excel(GDP_PATH / "World_Bank" / "BoP_WBankGDP_NA.xlsx")
for i, col in enumerate(gdp.columns):
    print(f"  {i}: {col}")
print("\nGDP sample:")
print(gdp.head())
