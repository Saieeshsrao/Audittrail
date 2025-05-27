import os
import pandas as pd
from openai import OpenAI
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client for RunPod
client = OpenAI(
    api_key=os.getenv('RUNPOD_API_KEY'),  # Your RunPod API key
    base_url=os.getenv('RUNPOD_BASE_URL')  # Your RunPod endpoint
)

# Function to process a single prompt
def process_single_prompt(input_text):
    try:
        response = client.chat.completions.create(
            model="Qwen/QwQ-32B-AWQ",  # Your model name
            messages=[
                {"role": "system", "content": "You are a strict compliance auditor specializing in SOP-log matching. Your job is to compare logs against SOPs and report only high-confidence violations."},
                {"role": "user", "content": input_text}
            ],
            temperature=0.2,
            top_p=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing prompt: {str(e)}")
        return f"Error: {str(e)}"

# Function to process all rows in a dataset
def process_dataset(input_file_path, output_file_path):
    df = pd.read_excel(input_file_path)
    if 'Input' not in df.columns:
        print("❌ 'Input' column not found in the Excel file.")
        return

    df['Generated_Output'] = None  # New column for responses

    for index, row in df.iterrows():
        print(f"Processing row {index + 1}/{len(df)}")

        input_text = row['Input']
        output = process_single_prompt(input_text)
        print(f"Output: {output}")

        df.at[index, 'Generated_Output'] = output

        time.sleep(1)  # Optional delay to avoid rate limits

        # Periodic backup
        if index % 10 == 0:
            df.to_excel(output_file_path, index=False)
            print(f"✅ Progress saved at row {index + 1}")

    # Final save
    df.to_excel(output_file_path, index=False)
    print(f"✅ Processing complete. Results saved to {output_file_path}")

# Optional cleaning function
def clean_generated_output(input_file, output_file):
    df = pd.read_excel(input_file)

    if 'Generated_Output' in df.columns:
        # Example: remove any unwanted AI formatting like "<think>" tags
        df['Generated_Output'] = df['Generated_Output'].astype(str).str.split('</think>').str[-1]
        df.to_excel(output_file, index=False)
        print(f"✅ Cleaned output saved to {output_file}")
    else:
        print("❌ 'Generated_Output' column not found in the Excel file.")

# Main execution
if __name__ == "__main__":
    input_file = "SOP_Log_Matching_UARW (1).xlsx"       # Your input file (must have an 'Input' column)
    output_file = "sop_verification_results_new.xlsx"          # Output file

    process_dataset(input_file, output_file)

    # Optional cleaning after generation
    clean_generated_output(output_file, "sop_cleaned_results_new.xlsx")
