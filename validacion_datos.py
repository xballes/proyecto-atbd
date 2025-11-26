import pandas as pd
from pathlib import Path

from great_expectations.dataset import PandasDataset
from great_expectations.render.renderer import ValidationResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView

# ============================
# 1) Cargar dataset
# ============================

DATA_PATH = Path("./ev_project/Electric_Vehicle_Population_Data.csv")
df = pd.read_csv(DATA_PATH)

print(f"Filas cargadas: {len(df)}")
print(df.dtypes)

# Dataset de Great Expectations (API clásica, sin DataContext)
gdf = PandasDataset(df)

# ============================
# 2) REGLAS DE VALIDACIÓN
# ============================

gdf.expect_table_row_count_to_be_between(100_000, 200_000)

expected_columns = [
    "VIN (1-10)", "County", "City", "State", "Postal Code",
    "Model Year", "Make", "Model", "Electric Vehicle Type",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility",
    "Electric Range", "Base MSRP", "Legislative District",
    "DOL Vehicle ID", "Vehicle Location", "Electric Utility",
    "2020 Census Tract",
]
gdf.expect_table_columns_to_match_set(expected_columns)

# --- 1) VIN ---
gdf.expect_column_values_to_not_be_null("VIN (1-10)")
gdf.expect_column_value_lengths_to_be_between("VIN (1-10)", 10, 10)
gdf.expect_column_values_to_match_regex("VIN (1-10)", r"^[A-Z0-9]+$")

# --- 2) County & City ---
for col in ["County", "City"]:
    gdf.expect_column_values_to_not_be_null(col)
    gdf.expect_column_values_to_be_of_type(col, "str")

# --- 3) State ---
valid_states = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY", "DC"
]

gdf.expect_column_values_to_not_be_null("State")
gdf.expect_column_value_lengths_to_be_between("State", 2, 2)
gdf.expect_column_values_to_match_regex("State", r"^[A-Z]{2}$")
gdf.expect_column_values_to_be_in_set("State", valid_states)

# --- 4) Postal Code ---
gdf.expect_column_values_to_be_between("Postal Code", 0, 99999)

# --- 5) Model Year ---
gdf.expect_column_values_to_be_between("Model Year", 1997, 2023)

# --- 6) Make & Model ---
gdf.expect_column_values_to_not_be_null("Make")
gdf.expect_column_values_to_not_be_null("Model", mostly=0.99)


# --- 7) EV Type ---
gdf.expect_column_values_to_be_in_set(
    "Electric Vehicle Type",
    [
        "Battery Electric Vehicle (BEV)",
        "Plug-in Hybrid Electric Vehicle (PHEV)",
    ],
)

# --- 8) CAFV ---
gdf.expect_column_values_to_be_in_set(
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility",
    [
        "Clean Alternative Fuel Vehicle Eligible",
        "Not eligible due to low battery range",
        "Eligibility unknown as battery range has not been researched",
    ],
)

# --- 9) Range ---
gdf.expect_column_values_to_be_between("Electric Range", 0, 400)

# --- 10) MSRP ---
gdf.expect_column_values_to_be_between("Base MSRP", 0, 1_000_000)

# --- 11) Legislative District ---
gdf.expect_column_values_to_be_between(
    "Legislative District", min_value=1, max_value=49, mostly=0.95
)

# --- 12) DOL Vehicle ID ---
gdf.expect_column_values_to_be_between("DOL Vehicle ID", min_value=1)
gdf.expect_column_proportion_of_unique_values_to_be_between(
    "DOL Vehicle ID", 0.999, 1.0
)

# --- 13) Location ---
gdf.expect_column_values_to_match_regex(
    "Vehicle Location", r".(,|\().", mostly=0.99
)

# --- 14) Electric Utility ---
gdf.expect_column_values_to_be_of_type("Electric Utility", "str", mostly=0.99)
gdf.expect_column_value_lengths_to_be_between(
    "Electric Utility", 3, None, mostly=0.99
)

# --- 15) Census Tract ---
gdf.expect_column_values_to_be_of_type("2020 Census Tract", "int64")
gdf.expect_column_values_to_match_regex(
    "2020 Census Tract",
    r"^\d{11}$",
    mostly=0.99   # ← se permite 1% fuera de rango
)


# ============================
# 3) Validación
# ============================

result = gdf.validate()
print("\nResumen de validación:")
print(result)

# ============================
# 4) HTML Report
# ============================

renderer = ValidationResultsPageRenderer()
document = renderer.render(result)
html = DefaultJinjaPageView().render(document)

output_dir = Path("results/validation")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "validacion_datos.html"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)


print(f"\nInforme generado en: {output_file}")
