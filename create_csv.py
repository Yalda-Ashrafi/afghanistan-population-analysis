import pandas as pd

# Read original dataset
df = pd.read_csv("world_population.csv")

# Create population.csv
population = df[["Country/Territory", "Continent", "2022 Population"]]
population.columns = ["country", "region", "population"]
population.to_csv("population.csv", index=False)

# Create area.csv
area = df[["Country/Territory", "Area (km²)"]]
area.columns = ["country", "area"]
area.to_csv("area.csv", index=False)

print("population.csv and area.csv created successfully!")