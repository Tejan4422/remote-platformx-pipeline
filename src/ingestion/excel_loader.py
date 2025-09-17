import pandas as pd

def load_excel(file_path: str) -> pd.DataFrame:
    """Load data from an Excel file and return it as a DataFrame."""
    df = pd.read_excel(file_path)
    return df