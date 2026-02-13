import pandas as pd

def to_float(val):
    if pd.isna(val):
        return 0.0
    return float(str(val).replace(",", "."))

def load_csv(file):
    file.seek(0)   # ✅ IMPORTANT
    df = pd.read_csv(file, sep=";", engine="python", encoding="utf-8-sig")

    df.columns = df.columns.str.strip()
    
   
   
    return df

