

import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    api_key="rpa_ROXJL6ZYMIOSDORA989IE314E6DW7DAM46LOAT2E14xv8r",  # Set your RunPod API key
    base_url="https://api.runpod.ai/v2/c5f4280t0dtrlx/openai/v1"  # Update with your endpoint URL
)

# Define your long prompt
prompt_text = r"""### **Instructions:**  
 1. **Analyze Each Log Entry Separately**  
   - If a log follows all SOP rules → Mark it **Compliant**.  
   - If a log deviates → **Mark it as a Violation and provide full details**.

2. **Severity Definitions (Follow Strictly):**  
   - **Critical**: Direct safety risk, regulatory non-compliance, or financial impact.  
   - **High**: Major process failure or procedural error affecting quality or efficiency.  
   - **Medium**: Minor process deviation but no immediate risk.  

3. **Output Structure (Strictly Follow This Table Format)**  
   - If violations exist: **Output exactly in this table format**  

     | Severity  | SOP Section | SOP Requirement  | Log Entry | Deviation Details | Confidence |
     |-----------|------------|------------------|-------------------|------------|
     | Critical/High/Medium  | X.X.X.X | 'Exact SOP text' | 'Log text' | Explanation | 95%+ |

   - If all logs are compliant:  

     | Status    | Details                                  |
     |-----------|------------------------------------------|
     | Compliant | All operations match SOP requirements    |

---

Logs:
--------------------------------
2023-02-20 | 08:45:00 | JohnDoe | Logged into the system.
2023-02-20 | 08:46:00 | JohnDoe | Accessed the "EDIT RECIPE" screen.
2023-02-20 | 08:47:00 | JohnDoe | Selected "COATING" icon.
2023-02-20 | 08:48:00 | JohnDoe | Operation type changed from "Conditioning Coater" to "Film Coating".
2023-02-20 | 08:49:00 | JohnDoe | Operation name changed from "Coating" to "Pre-warming and Coating".
2023-02-20 | 08:50:00 | JohnDoe | Skipped renaming the recipe (SOP requires renaming).
2023-02-20 | 08:51:00 | JohnDoe | Saved the new recipe without authorization (SOP requires authorization before saving).
2023-02-20 | 08:52:00 | JohnDoe | Authorized the recipe "ProductXRecipe" for production.
2023-02-20 | 08:53:00 | JohnDoe | Batch number changed from "B001" to "B002" for recipe "ProductXRecipe".
2023-02-20 | 08:54:00 | JohnDoe | Lot number changed from "L001" to "L002" for recipe "ProductXRecipe".
2023-02-20 | 08:55:00 | JohnDoe | Product name changed from "Generic Product" to "Product X" for recipe "ProductXRecipe".
2023-02-20 | 08:56:00 | JohnDoe | Solution quantity changed from 1000 liters to 1200 liters for recipe "ProductXRecipe".
2023-02-20 | 08:57:00 | JohnDoe | Lot size changed from 500 units to 600 units for recipe "ProductXRecipe".
2023-02-20 | 08:58:00 | JohnDoe | Process parameter "Inlet temperature" changed from 25 degrees to 30 degrees for "Pre-warming" operation.
2023-02-20 | 08:59:00 | JohnDoe | Added an unauthorized operation "Extra Drying" (not listed in SOP operations).
2023-02-20 | 09:00:00 | JohnDoe | Process parameter "Spraying time" changed from 10 minutes to 12 minutes for "Coating" operation.
2023-02-20 | 09:01:00 | JohnDoe | Process parameter "Drying temperature" changed from 60 degrees to 65 degrees for "Drying" operation.
2023-02-20 | 09:02:00 | JohnDoe | Process parameter "Cooling time" changed from 15 minutes to 18 minutes for "Cooling" operation.
2023-02-20 | 09:03:00 | JohnDoe | Failed to press 'finish' icon to finalize the recipe (SOP requires pressing 'finish').
2023-02-20 | 09:04:00 | JohnDoe | Logged out of the system without completing the batch setup (SOP requires completing batch setup).
-------------------------------

SOP:
--------------------------------
6.3.2.5	Select the 'login' icon, a login screen appears. Fill the suitable 
details and log in.
6.3.2.6 .1	Press the “EDIT RECIPE’ icon screen. 
6.3.2.6 .2	Then press the “COATING” icon. 
6.3.2.6 .3	Select the operation type from the list like Charging, Conditioning Coater, Film Coating, conditioning, Discharge Front and Stop Coater. 
6.3.2.6 .4	Edit the Operation name as per Batch Production   and   Control   Record (BPCR) like Charging, Pre-warming, Coating, Drying and Cooling, Discharge and Stop Coater. 
6.3.2.6 .5	Press ‘rename' icon and enter product name to save the recipe with product name.
6.3.2.6 .6	Press the 'save' icon. 
6.3.2.6 .7	Press the “AUTHORIZE” icon for authorizing the recipe. 
6.3.2.6 .8	Select the Product, press the 'authorize' icon and authorize   the   product   for   production. After authorization of product press 'back' icon to go the previous screen. 
6.3.2.6 .9	Press the Batch (F2) icon.
6.3.2.6 .10 Select the “I want to produce” popup icon and press the 'next' icon to select the recipe, select the recipe and then press the 'next' icon.
6.3.2.6 .11	 Enter the Batch number & lot no. as per BPCR and press the 'next' icon. 
6.3.2.6 .12 Enter the Product name, solution quantity and lot size as per BPCR and press the 'next' icon.
6.3.2.6 .13 If everything is ok select the 'finish' icon to save the recipe.
6.3.2.6 .14 Press   the 'edit' icon   to   edit   the   process parameters as per BPCR in the selected operation phase if required. Press exit icon after setting the data in every process operation to go to the next process operation. 
• For Charging
• For Pre-Warming
• For Spraying
• For Drying
• For Cooling 
• For Discharging
• For Stop Coater
--------------------------------

**Rules:**  
 **Do NOT modify the table format.**  
 **Only report deviations ≥95% confidence.**  
 **Quote exact text from logs and SOPs.**  
 **Reject uncertain findings.**
"""

# Create a completion request using the OpenAI client
response = client.chat.completions.create(
    model="Qwen/QwQ-32B-AWQ",  # Replace with your model's name
    messages=[{"role": "system", "content": "You are an AI trained to analyze SOP compliance."},
              {"role": "user", "content": prompt_text}],
    temperature=0
)

# Print the entire response
print(response)

# Extract and print the generated response
if response.choices:
    print("Response Text:")
    print(response.choices[0].message.content)

import os
import pandas as pd
from openai import OpenAI
import time

# Initialize the OpenAI client
client = OpenAI(
    api_key="rpa_ROXJL6ZYMIOSDORA989IE314E6DW7DAM46LOAT2E14xv8r",
    base_url="https://api.runpod.ai/v2/c5f4280t0dtrlx/openai/v1"
)

def process_single_prompt(input_text):
    try:
        response = client.chat.completions.create(
            model="Qwen/QwQ-32B-AWQ",
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

def process_dataset(input_file_path, output_file_path):
    # Read the dataset
    df = pd.read_excel(input_file_path)  # or pd.read_csv if it's a CSV file
    
    # Add a new column for the API responses
    df['Generated_Output'] = None
    
    # Process each row
    for index, row in df.iterrows():
        print(f"Processing row {index + 1}/{len(df)}")
        
        # Get the input text from the 'Input' column
        input_text = row['Input']  # Adjust column name if different
        
        # Process the prompt
        output = process_single_prompt(input_text)
        
        # Store the result
        df.at[index, 'Generated_Output'] = output
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
        
        # Save progress periodically
        if index % 10 == 0:
            df.to_excel(output_file_path, index=False)
            print(f"Progress saved at row {index + 1}")
    
    # Save final results
    df.to_excel(output_file_path, index=False)
    print(f"Processing complete. Results saved to {output_file_path}")

if __name__ == "__main__":
    input_file = "SOP_Log_Verification_Dataset.xlsx"  # Replace with your input file path
    output_file = "sop_verification_results.xlsx"
    
    process_dataset(input_file, output_file)



def clean_generated_output(input_file, output_file):
    # Load the Excel file
    df = pd.read_excel(input_file)
    
    # Ensure 'Generated_Output' column exists
    if 'Generated_Output' in df.columns:
        df['Generated_Output'] = df['Generated_Output'].astype(str).str.split('</think>').str[-1]
    else:
        print("Column 'Generated_Output' not found in the Excel file.")
        return
    
    # Save the modified DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"Processed file saved as {output_file}")

# Example usage
input_file = "sop_verification_results.xlsx"  # Replace with your actual input file
output_file = "output1.xlsx"  # Replace with desired output file name
clean_generated_output(input_file, output_file)
