import streamlit as st
import pandas as pd
import re
import pdfplumber
import ollama
from io import BytesIO, StringIO

###############################################
# Utility Functions
###############################################

def get_machine_activity_pairs(df, machine_name):
    pattern = re.compile(rf'\b{re.escape(machine_name)}\b', re.IGNORECASE)
    results = []
    
    if "Activity" not in df.columns:
        raise ValueError("The column 'Activity' is missing from the Excel file.")

    for index, row in df.iterrows():
        activity_description = str(row["Activity"])
        if pattern.search(activity_description):
            results.append((activity_description, index + 2))
    return results

def find_machine_rows(excel_file, machine_name):
    df = pd.read_excel(excel_file)
    return get_machine_activity_pairs(df, machine_name)

###############################################
# SOP Extraction Functions
###############################################

def extract_text_from_pdf(pdf_source):
    try:
        full_text = ""
        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        return full_text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_section(text, section_identifier="6.3.1"):
    pattern = re.compile(
        rf"({re.escape(section_identifier)}[\s\S]*?)(?=6\.3\.2|$)",
        re.DOTALL
    )
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    else:
        idx = text.find(section_identifier)
        return text[idx:].strip() if idx != -1 else f"Section {section_identifier} not found."

def get_machine_procedure(pdf_source, machine_name, section_identifier="6.3.1"):
    full_text = extract_text_from_pdf(pdf_source)
    return extract_section(full_text, section_identifier) if full_text else "Failed to extract SOP text."

###############################################
# LLM Comparison Function with Table Format
###############################################

def compare_logs_and_sop(sop_text, log_text):
    prompt = f"""
You are a quality assurance specialist conducting SOP-log compliance analysis. 
Return findings STRICTLY in this format:

**Response Template**
If anomalies found:

| Severity               | SOP Section | SOP Requirement  | Log Entry | Deviation Details | Confidence|
|------------------------|-------------|------------------|-----------|-------------------|-----------|
| [Critical/High/Medium] | Section X.X | "Exact SOP text" | "Log text"| Specific mismatch | 95%+      |

If no anomalies:

| Status | Details                                  |
|--------|------------------------------------------|
| Compliant | All operations match SOP requirements |

Analysis Rules:
1. Only show rows with ≥95% confidence in deviation
2. Severity must reference SOP consequence guidelines
3. Quote exact text from both documents
4. Empty cells if field doesn't apply for compliant cases
5. Never modify this table structure
6. Reject uncertain findings completely

SOP:
--------------------------------
{sop_text}
--------------------------------

Logs:
--------------------------------
{log_text}
--------------------------------
"""
    
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

###############################################
# Streamlit UI with Table Display
###############################################

def main():
    st.title("SOP Compliance Analyzer")
    
    st.sidebar.header("File Upload")
    log_file = st.sidebar.file_uploader("Upload Log (Excel)", type=["xlsx"])
    sop_file = st.sidebar.file_uploader("Upload SOP (PDF)", type=["pdf"])
    
    machine_name = st.sidebar.text_input("Machine Name", "PAM GLATT")
    section_identifier = st.sidebar.text_input(
        "SOP Section Identifier", 
        "6.3.1 Operating procedure of Autocoater (PAM GLATT)"
    )
    
    if log_file and sop_file:
        st.header("Analysis Results")
        
        # Process Log File
        try:
            df = pd.read_excel(log_file)
            machine_rows = find_machine_rows(log_file, machine_name)
            
            if not machine_rows:
                st.error("No matching log entries found")
                return
                
            row_numbers = [row[1] for row in machine_rows]
            filtered_df = df.iloc[min(row_numbers)-2 : max(row_numbers)-1]
            log_text = filtered_df.to_csv(index=False)
            
        except Exception as e:
            st.error(f"Log processing error: {e}")
            return

        # Process SOP File
        sop_text = get_machine_procedure(sop_file, machine_name, section_identifier)
        if "not found" in sop_text or "Failed" in sop_text:
            st.error(sop_text)
            return

        # LLM Analysis
        with st.spinner("Conforming compliance analysis..."):
            try:
                result = compare_logs_and_sop(sop_text, log_text)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

        # Display Results
        if "|" in result:
            try:
                # Clean and parse table
                cleaned = re.sub(r'(\n\s*){2,}', '\n', result)  # Remove extra newlines
                cleaned = re.sub(r'[^\S\n]+\|', '|', cleaned)   # Fix column spacing
                
                df_result = pd.read_csv(
                    StringIO(cleaned),
                    sep="|",
                    skipinitialspace=True
                ).dropna(axis=1, how='all').iloc[1:]  # Skip header separator row
                
                # Formatting
                if 'Severity' in df_result.columns:
                    severity_colors = {
                        'Critical': 'red',
                        'High': 'orange',
                        'Medium': '#FFCC00'  # Darker yellow
                    }
                    df_result['Severity'] = df_result['Severity'].str.strip().apply(
                        lambda x: f"<span style='color: {severity_colors.get(x, 'black')}; font-weight: bold'>{x}</span>"
                    )
                
                # Display table
                st.markdown(df_result.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                # Show raw data toggle
                with st.expander("View Raw Data"):
                    st.subheader("Filtered Log Entries")
                    st.dataframe(filtered_df)
                    st.subheader("SOP Section")
                    st.text(sop_text)
                    
            except Exception as e:
                st.error(f"Result parsing error: {e}")
                st.text_area("Raw Analysis Output", value=result, height=300)
        else:
            st.success("No Anomalies Detected")
            st.markdown(f"```\n{result}\n```")

if __name__ == "__main__":
    main()