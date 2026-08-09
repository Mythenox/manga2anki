import pandas as pd
import re

df = pd.read_csv("jlpt_vocab_all_cleaned.csv")

"""for row in df.itertuples(index=True):
    if isinstance(row.reading, str):
        df.at[row.Index, "reading"] = re.sub(r"\(([^)]*)\)", "", row.reading)
    if isinstance(row.expression, str):
        df.at[row.Index, "expression"] = re.sub(r"\(([^)]*)\)", "", row.expression)"""

df = df.drop_duplicates()


df.to_csv("jlpt_vocab_all_drop_dups.csv", index=False)

#\(([^)]*)\)