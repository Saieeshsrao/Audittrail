import pandas as pd
import re

def get_machine_activity_pairs(df, machine_name):
    """
    Searches for the machine name in the 'Activity' column using regex 
    and returns matching activity descriptions along with row numbers.
    """
    results = []
    pattern = re.compile(rf'\b{re.escape(machine_name)}\b', re.IGNORECASE)

    if "Activity" not in df.columns:
        raise ValueError("The column 'Activity' is missing from the Excel file.")

    for index, row in df.iterrows():
        activity_description = str(row["Activity"])
        if pattern.search(activity_description):
            results.append((activity_description, index + 2))
    return results

def find_machine_rows(excel_file, machine_name):
    """
    Reads an Excel file and searches for rows containing the machine name in the 'Activity' column.
    """
    df = pd.read_excel(excel_file)
    return get_machine_activity_pairs(df, machine_name)

def get_rows_between_activities(df, start_activity, end_activity):
    """
    Get rows between two specified activities (inclusive).
    """
    if "Activity" not in df.columns:
        raise ValueError("The column 'Activity' is missing from the Excel file.")
    
    # Find the rows containing start and end activities
    start_idx = None
    end_idx = None
    
    for idx, row in df.iterrows():
        activity = str(row["Activity"])
        if start_activity.lower() in activity.lower() and start_idx is None:
            start_idx = idx
        if end_activity.lower() in activity.lower():
            end_idx = idx
            # Don't break here in case there are multiple matches - we want the last one
    
    if start_idx is None or end_idx is None:
        raise ValueError(f"Could not find {'start' if start_idx is None else 'end'} activity in the log file")
    
    # Return the slice of rows between start and end (inclusive)
    return df.iloc[start_idx:end_idx + 1]