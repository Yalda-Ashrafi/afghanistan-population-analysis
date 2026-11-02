from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = DATA_DIR / "result.xlsx"

print("=" * 72)
print("AFGHANISTAN POPULATION ANALYSIS")
print("=" * 72)

# (1) Load the two datasets using pandas.
population = pd.read_csv(DATA_DIR / "population.csv")
area = pd.read_csv(DATA_DIR / "area.csv")
print("\n(1) Load population.csv and area.csv")
print(f"Population records: {len(population)}")
print(f"Area records: {len(area)}")
print("Population columns:", ", ".join(population.columns))
print("Area columns:", ", ".join(area.columns))

# (2) Merge the datasets using the country column.
df = population.merge(area, on="country", how="inner", validate="one_to_one")
if len(df) != len(population):
    raise ValueError("Some countries in population.csv have no matching area.csv record.")
print("\n(2) Merge datasets using 'country'")
print(f"Merged rows: {len(df)}")
print(df[["country", "region", "population", "area"]].head().to_string(index=False))

# (3) Create population density as population divided by area.
if (df["area"] <= 0).any():
    raise ValueError("Area values must be greater than zero to calculate population density.")
df["population_density"] = df["population"] / df["area"]
print("\n(3) Calculate population density = population / area")
print(df[["country", "population", "area", "population_density"]].head().to_string(index=False))

# (4) Compute total population by region.
region_summary = (
    df.groupby("region", as_index=False)["population"]
    .sum()
    .rename(columns={"population": "region_population"})
)
print("\n(4) Total population by region")
print(region_summary.to_string(index=False))

# (5) Extract Afghanistan's population.
afghanistan = df.loc[df["country"] == "Afghanistan", "population"]
if len(afghanistan) != 1:
    raise ValueError("Expected exactly one Afghanistan record in the merged data.")
afghanistan_population = int(afghanistan.iloc[0])
print("\n(5) Afghanistan population")
print(f"{afghanistan_population:,}")

# (6) Add Afghanistan's population and its ratio to each region.
region_summary["afghanistan_population"] = afghanistan_population
region_summary["afghanistan_population_ratio"] = (
    region_summary["afghanistan_population"] / region_summary["region_population"]
)
df = df.merge(
    region_summary[
        ["region", "region_population", "afghanistan_population_ratio"]
    ],
    on="region",
    how="left",
    validate="many_to_one",
)
print("\n(6) Afghanistan population ratio for each region")
print(
    region_summary[
        ["region", "region_population", "afghanistan_population_ratio"]
    ].to_string(
        index=False,
        formatters={"afghanistan_population_ratio": "{:.2%}".format},
    )
)

# (7) Save the analysis in an Excel workbook.
asia_summary = region_summary.loc[region_summary["region"] == "Asia"]
if asia_summary.empty:
    raise ValueError("Asia is not present in the region column.")
asia_population = int(asia_summary["region_population"].iloc[0])
asia_ratio = afghanistan_population / asia_population

# The source files contain continent-level regions, not Central Asia subregions.
conclusion = (
    "The supplied data classifies Afghanistan as part of Asia and does not "
    "provide a Central Asia category. Afghanistan's population is "
    f"{asia_ratio:.2%} of Asia's total population. Therefore, a "
    "Central Asia-specific population share cannot be calculated from these "
    "files alone."
)

with pd.ExcelWriter(OUTPUT_PATH) as writer:
    df.to_excel(writer, sheet_name="Population Data", index=False)
    region_summary.to_excel(writer, sheet_name="Region Summary", index=False)
    pd.DataFrame({"Conclusion": [conclusion]}).to_excel(
        writer, sheet_name="Conclusion", index=False
    )
print(f"\n(7) Excel workbook saved: {OUTPUT_PATH}")
print("Workbook sheets: Population Data, Region Summary, Conclusion")

# (8) State the conclusion supported by the supplied data.
print("\n(8) Conclusion")
print(conclusion)
