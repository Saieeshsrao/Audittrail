import pandas as pd
from utils import find_machine_rows
from sop_extractor import get_machine_procedure
excel_file_path = "log.xlsx"
machine_name = "PAM GLATT"
new_log_file_path = "filtered_log.xlsx" 
pdf_file_path = "SOP.pdf" # New log file
section_name='6.3.1 Operating procedure of Autocoater (PAM GLATT)'

# Call the function and get matching rows
result = find_machine_rows(excel_file_path, machine_name)
print(result)

# Extract row numbers
row_numbers = [row[1] for row in result]

if row_numbers:  # Ensure there are matching rows
    start = min(row_numbers)
    end = max(row_numbers)

    print(f"Rows: {start} to {end}")

    # Load original Excel file
    df = pd.read_excel(excel_file_path)

    # Filter rows within the start-end range (Excel rows are 1-based, Pandas uses 0-based index)
    filtered_df = df.iloc[start - 2 : end - 1]  # Adjust for header offset

    # Save the new filtered log file
    filtered_df.to_excel(new_log_file_path, index=False)
    print(f"Filtered log saved as {new_log_file_path}")
else:
    print("No matching rows found.")

procedure_text =get_machine_procedure(pdf_file_path, machine_name) #get_machine_procedure(pdf_file_path, machine_name)

# Print the result
print(f"Operational Procedure for {machine_name}:\n")
print(procedure_text)
