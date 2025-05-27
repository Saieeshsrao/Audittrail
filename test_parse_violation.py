import pandas as pd
from compare_logs_sop import parse_violation_report

def test_parse_violation():
    # Set pandas display options to show complete content
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    # Sample violation report text
    sample_text = """
| Severity | SOP Section | SOP Requirement | Log Entry (Row #) | Deviation Details | Confidence |
|-----------|-------------|------------------|-------------------|-------------------|------------|
| Critical | 6.3.1.2 | "Ensure that the compressed air pressure is NLT 4.0 Kg/cm²." | "2025-01-28 | 08:20:00 | John Doe | Compressed air pressure verified. (Air Pressure changed from Not Checked to 1 kg/cm²)" | 100% |
| High | 6.3.1.5.7-6.3.1.5.11 | "Use tared sample polybags for weighing the coating solution for verification of the spray rate... Record the average spray rate..." | "2025-01-28 | 08:35:00 | John Doe | Spray Rate changed from Not Set to 30 mL/min per gun" | 100% |
| High | 6.3.1.5.7-6.3.1.5.11 | "Use tared sample polybags for weighing the coating solution for verification of the spray rate... Record the average spray rate..." | "2025-01-28 | 10:00:00 | John Doe | Spray rate adjusted for uniform coating. (Spray Rate changed from 30 mL/min per gun to 32 mL/min per gun)" | 100% |
| High | 6.3.1.6.1 | "Verify the spray pattern by setting atomization pressure as per the Batch Production and Control Record... Hold the stainless-steel tray in front of the guns..." | "2025-01-28 | 08:45:00 | John Doe | Spray pattern verified via SCADA. (Spray Pattern changed from Not Verified to OK)" | 100% |
| Critical | 6.3.1.12.2 | "Stop the machine by pressing stop key and take out the spray gun arm assembly." | "2025-01-28 | 11:30:00 | John Doe | Process paused via SCADA for cleaning. (Status changed from Batch In Progress to Paused)" | 100% |
"""

    # Parse the violation report
    df = parse_violation_report(sample_text)
    
    # Print the DataFrame with complete content
    print("\nComplete Parsed DataFrame:")
    print("=" * 150)  # Separator line
    print(df.to_string())
    print("=" * 150)  # Separator line
    
    # Print DataFrame info
    print("\nDataFrame Info:")
    print(df.info())
    
    # Print DataFrame shape
    print("\nDataFrame Shape:", df.shape)
    
    # Print column names
    print("\nColumn Names:", df.columns.tolist())
    
    return df

if __name__ == "__main__":
    df = test_parse_violation() 