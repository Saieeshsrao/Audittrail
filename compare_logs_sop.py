# import ollama
# import re
# import pandas as pd
# def parse_violation_report(response_text):
#     """
#     Parses the violation report and converts it into a structured DataFrame.
#     """

#     # Extracting table data using regex
#     table_pattern = re.findall(r"\| (.*?) \|", response_text)

#     if not table_pattern:
#         print("No table data found.")
#         return None

#     # Splitting the extracted data into rows based on "|"
#     rows = [row.split(" | ") for row in response_text.split("\n") if "|" in row]

#     # Cleaning up headers and removing empty rows
#     if len(rows) > 1:
#         headers = [col.strip() for col in rows[0]]
#         data = [[col.strip() for col in row] for row in rows[1:] if len(row) == len(headers)]
#     else:
#         print("No structured table data found.")
#         return None

#     # Creating a DataFrame
#     df = pd.DataFrame(data, columns=headers)
    
#     return df

# def compare_logs_and_sop(sop_text, log_text, model_name):
#     """
#     Compares the SOP text with the log text using LLM and returns anomalies.
#     """

#     prompt = f"""
# ### **Role:**  
# You are a strict compliance auditor specializing in **SOP-log matching**. Your job is to **compare logs against SOPs** and report **only high-confidence violations** (≥95% certainty).

# ---

# ### **Instructions:**  
# 1. **Analyze Each Log Entry Separately**  
#    - If a log follows all SOP rules → Mark it **Compliant**.  
#    - If a log deviates → **Mark it as a Violation and provide full details**.

# 2. **Severity Definitions (Follow Strictly):**  
#    - **Critical**: Direct safety risk, regulatory non-compliance, or financial impact.  
#    - **High**: Major process failure or procedural error affecting quality or efficiency.  
#    - **Medium**: Minor process deviation but no immediate risk.  

# 3. **Output Structure (Strictly Follow This Table Format)**  
#    - If violations exist: **Output exactly in this table format**  

#      | Severity               | SOP Section | SOP Requirement  | Log Entry (Row #) | Deviation Details | Confidence |
#      |------------------------|-------------|------------------|-------------------|-------------------|-----------|
#      | Critical/High/Medium  | X.X | "Exact SOP text" | "Log text (Row #X)" | Explanation | 95%+ |

#    - If all logs are compliant:  

#      | Status    | Details                                  |
#      |-----------|------------------------------------------|
#      | Compliant | All operations match SOP requirements    |

# ---
# Logs:
# --------------------------------
# {log_text}
# --------------------------------

# SOP:
# --------------------------------
# {sop_text}
# --------------------------------

# **Rules:**  
# ✅ **Do NOT modify the table format.**  
# ✅ **Only report deviations ≥95% confidence.**  
# ✅ **Quote exact text from logs and SOPs.**  
# ✅ **Reject uncertain findings.**  
# """


# #     prompt = f"""
# # You are a quality assurance specialist conducting SOP-log compliance analysis. 
# # Return findings STRICTLY in this format:

# # **Response Template**
# # If anomalies found:

# # | Severity               | SOP Section | SOP Requirement  | Log Entry | Deviation Details | Confidence|
# # |------------------------|-------------|------------------|-----------|-------------------|-----------|
# # | [Critical/High/Medium] | Section X.X | "Exact SOP text" | "Log text"| Specific mismatch | 95%+      |

# # If no anomalies:

# # | Status | Details                                  |
# # |--------|------------------------------------------|
# # | Compliant | All operations match SOP requirements |

# # Analysis Rules:
# # 1. Only show rows with ≥95% confidence in deviation
# # 2. Severity must reference SOP consequence guidelines
# # 3. Quote exact text from both documents
# # 4. Empty cells if field doesn't apply for compliant cases
# # 5. Never modify this table structure
# # 6. Reject uncertain findings completely

# # SOP:
# # --------------------------------
# # {sop_text}
# # --------------------------------

# # Logs:
# # --------------------------------
# # {log_text}
# # --------------------------------
# # """

#     response = ollama.chat(
#         model=model_name,
#         messages=[{"role": "user", "content": prompt}],
#         options={ 'num_ctx': 4096,  # More context memory
#         'temperature': 0.2,  # Less randomness
#         'top_p': 0.8,},
        
#     )
#     df= parse_violation_report(response["message"]["content"])

#     return df

import re
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def parse_violation_report(response_text):
    """
    Parses the violation report and converts it into a structured DataFrame.
    """
    # Clean the response - extract content after </think> if it exists
    if "</think>" in response_text:
        response_text = response_text.split("</think>")[-1].strip()
    
    # Extracting table rows using regex
    rows = [row.split(" | ") for row in response_text.split("\n") if "|" in row]

    if len(rows) < 2:  # At least headers + one row required
        print("No structured table data found.")
        return pd.DataFrame()  # Return an empty DataFrame instead of None

    # Extracting headers and cleaning rows
    headers = [col.strip() for col in rows[0]]
    data = []
    for row in rows[1:]:
        if len(row) == len(headers):
            cleaned_row = [col.strip() for col in row]
            # Only add rows that contain actual data (not just empty strings)
            if any(col != "" for col in cleaned_row):
                data.append(cleaned_row)

    # Creating a DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df


def compare_logs_and_sop(sop_text, log_text, model_name=None):
    """
    Compares the SOP text with the log text using RunPod API and returns anomalies.
    """
    # Initialize the OpenAI client with RunPod details from environment variables
    client = OpenAI(
        api_key=os.getenv('RUNPOD_API_KEY'),
        base_url=os.getenv('RUNPOD_BASE_URL')
    )
    prompt = f"""
### ROLE:
You are a **compliance auditor AI** specializing in **SOP-log matching**.  
Your job is to **strictly compare each log entry** against the **Standard Operating Procedure (SOP)** and identify **only high-confidence violations (≥95%)**.

---

### TASK INSTRUCTIONS:

1. **Process Each Log Entry Independently**
   - If a log fully aligns with relevant SOP rules → Mark as **Compliant**.
   - If a log violates any SOP requirement → Mark as **Violation**, with full details.
   - Ignore physical/manual actions described in SOP that do not appear in logs unless explicitly logged.

2. **Violation Reporting Criteria**
   - Only report deviations that you are **≥95% confident** are genuine violations.
   - Use **exact matching** of SOP phrases and log actions — no assumptions or inferred behavior.
   - **Reject uncertain or borderline cases** — this audit is only for clear, high-confidence violations.

3. **Violation Severity Classification**
   - **Critical** → Safety risk, regulatory non-compliance, or direct financial impact.
   - **High** → Major process or procedural failure that affects quality, traceability, or efficiency.
   - **Medium** → Minor procedural deviation with no immediate safety or compliance risk.

---

### OUTPUT FORMAT (STRICT):
- If there are violations, report them **exactly in the table below** (do not change headers or structure):

  | Severity  | SOP Section | SOP Requirement  | Log Entry (Row #) | Deviation Details | Confidence |
  |-----------|-------------|------------------|-------------------|-------------------|------------|
  | Critical/High/Medium | X.X | "Exact text from SOP" | "Exact log entry (Row #X)" | Explain how it deviates | 95%+ |

- If **all logs match the SOP**, return this table exactly:

  | Status    | Details                               |
  |-----------|----------------------------------------|
  | Compliant | All operations match SOP requirements |

---

### EXCLUSION RULE:
Do NOT report violations if:
- The SOP refers to **physical/manual actions** (e.g., "shut the valve", "clean surface") that are **not logged** and **not expected in log files**.

---

### INPUT DATA

Logs:
--------------------------------
{log_text}
--------------------------------

SOP:
--------------------------------
{sop_text}
--------------------------------

"""

#     prompt = f"""
# ### **Role:**  
# You are a strict compliance auditor specializing in **SOP-log matching**. Your job is to **compare logs against SOPs** and report **only high-confidence violations**.

# ---

# ### **Instructions:**  
# 1. **Analyze Each Log Entry Separately**  
#    - If a log follows all SOP rules → Mark it **Compliant**.  
#    - If a log deviates → **Mark it as a Violation and provide full details**.

# 2. **Severity Definitions (Follow Strictly):**  
#    - **Critical**: Direct safety risk, regulatory non-compliance, or financial impact.  
#    - **High**: Major process failure or procedural error affecting quality or efficiency.  
#    - **Medium**: Minor process deviation but no immediate risk.  

# 3. **Output Structure (Strictly Follow This Table Format)**  
#    - If violations exist: **Output exactly in this table format**  

#      | Severity  | SOP Section | SOP Requirement  | Log Entry (Row #) | Deviation Details | Confidence |
#      |-----------|------------|------------------|-------------------|-------------------|------------|
#      | Critical/High/Medium  | X.X | "Exact SOP text" | "Log text (Row #X)" | Explanation | 95%+ |

#    - If all logs are compliant:  

#      | Status    | Details                                  |
#      |-----------|------------------------------------------|
#      | Compliant | All operations match SOP requirements    |

# ---
# Logs:
# --------------------------------
# {log_text}
# --------------------------------

# SOP:
# --------------------------------
# {sop_text}
# --------------------------------

# **Rules:**  
# **Do NOT modify the table format.**  
# **Only report deviations ≥95% confidence.**  
# **Quote exact text from logs and SOPs.**  
# **Reject uncertain findings.**  
# **Do not give anomalies which are physical actions in nature which are defined in the SOP and not present in the logs** 
# """

    try:
        # Process the prompt using RunPod API
        response = client.chat.completions.create(
            model="Qwen/QwQ-32B-AWQ",
            messages=[
                {"role": "system", "content": "You are a strict compliance auditor specializing in SOP-log matching. Your job is to compare logs against SOPs and report only high-confidence violations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            top_p=0.8
        )
        
        result = response.choices[0].message.content
        
        # Extract content after </think> if it exists
        if "</think>" in result:
            result = result.split("</think>")[-1].strip()
            
        return result
    except Exception as e:
        return f"Error processing analysis: {str(e)}"
   
   
