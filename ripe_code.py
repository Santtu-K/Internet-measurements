import os.path
import pandas as pd

file_path = "public_probes.csv"
exi = os.path.exists(file_path)

if exi:
    print("Data exists")
    df = pd.read_csv(file_path)

    relevant = df[df["country_code"].value_counts() > 50] # relevant countries (more than 50 probes)

    country_counts = relevant["country_code"].value_counts()


    print(country_counts)
    print(df.head(3))
else:
    print("Data does not exist")