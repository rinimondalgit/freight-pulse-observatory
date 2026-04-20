import pandas as pd
if __name__ == "__main__":
    df = pd.read_csv("shipments.csv")
    print(df.head())
    print(df.shape)
