import streamlit as st
import pandas as pd
from utils import find_machine_rows
from sop_extractor import get_machine_procedure
from compare_logs_sop import compare_logs_and_sop
from utils import get_rows_between_activities

# def main():
#     st.title("SOP vs Log Comparison Interface")
    
#     st.sidebar.header("Upload Your Files")
#     log_file = st.sidebar.file_uploader("Upload Log File (Excel)", type=["xlsx"])
#     sop_file = st.sidebar.file_uploader("Upload SOP File (PDF)", type=["pdf"])
    
#     machine_name = st.sidebar.text_input("Machine Name", "PAM GLATT")
#     section_identifier = st.sidebar.text_input(
#         "SOP Section Identifier", 
#         "6.3.1 Operating procedure of Autocoater (PAM GLATT)"
#     )
    
#     model_options = {
#         "Llama 3.2": "llama3.2",
#         "DeepSeek": "deepseek-r1:7b"
#     }
#     selected_model = st.sidebar.selectbox("Select LLM Model", list(model_options.keys()))

#     if log_file and sop_file:
#         st.header("Processing Files")

#         # ----- Process Log File -----
#         try:
#             df = pd.read_excel(log_file)
#         except Exception as e:
#             st.error(f"Error reading Excel file: {e}")
#             return

#         st.write("Total rows in log file:", df.shape[0])

#         # Find machine activity rows
#         try:
#             machine_rows = find_machine_rows(log_file, machine_name)
#         except Exception as e:
#             st.error(f"Error processing log file: {e}")
#             return

#         if not machine_rows:
#             st.error("No matching rows found in the log file for the machine provided.")
#             return

#         st.write("Matching rows (activity and Excel row number):", machine_rows)
#         row_numbers = [row[1] for row in machine_rows]
#         start, end = min(row_numbers), max(row_numbers)
#         st.write(f"Filtering rows from: {start} to {end}")

#         filtered_df = df.iloc[start - 2:end - 1]  # Adjusting for header offset
#         log_text = "\n".join(filtered_df.astype(str).apply(lambda x: ' | '.join(x), axis=1))

#         # ----- Extract SOP Section -----
#         sop_text = get_machine_procedure(sop_file, machine_name, section_identifier)
#         st.subheader("Extracted SOP Section")
#         st.text_area("SOP Section", sop_text, height=200)

#         # ----- Compare Logs with SOP -----
#         st.subheader("Comparison Results")
#         model_name = model_options[selected_model]
#         comparison_results = compare_logs_and_sop(sop_text, log_text, model_name)
#         st.text_area("Comparison Results", comparison_results, height=400)

# if __name__ == "__main__":
#     main()



# def main():
#     st.title("SOP vs Log Comparison Interface")
    
#     # Sidebar inputs
#     st.sidebar.header("Upload Your Files")
#     log_file = st.sidebar.file_uploader("Upload Log File (Excel)", type=["xlsx"])
#     sop_file = st.sidebar.file_uploader("Upload SOP File (PDF)", type=["pdf"])
    
#     machine_name = st.sidebar.text_input("Machine Name", "")
    
#     st.sidebar.subheader("Log Filter Settings")
#     start_activity = st.sidebar.text_input("Start Activity", "")
#     end_activity = st.sidebar.text_input("End Activity", "")
    
#     st.sidebar.subheader("SOP Settings")
#     section_identifier = st.sidebar.text_input(
#         "SOP Section Identifier", 
#         ""
#     )
    
#     model_options = {
#         "Llama 3.2": "llama3.2",
#         "DeepSeek": "deepseek-r1:7b"
#     }
#     selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))
    
#     # Submit button
#     submit_button = st.sidebar.button("Process Files")
    
#     # Only process if files are uploaded and submit is clicked
#     if log_file and sop_file:
#         if submit_button:
#             st.header("Processing Files")
            
#             try:
#                 with st.spinner('Processing files...'):
#                     df = pd.read_excel(log_file)
#                     filtered_df = get_rows_between_activities(df, start_activity, end_activity)
#                     st.write(f"Found {len(filtered_df)} rows between specified activities")
                    
#                     # Convert filtered rows to text format
#                     log_text = "\n".join(filtered_df.astype(str).apply(lambda x: ' | '.join(x), axis=1))
                    
#                     # Extract SOP section
#                     sop_text = get_machine_procedure(sop_file, machine_name, section_identifier)
                    
#                     if not sop_text:
#                         st.error("Could not find specified SOP section")
#                         return
                    
#                     # Display results
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         st.subheader("Filtered Log Entries")
#                         st.dataframe(filtered_df)
                    
#                     with col2:
#                         st.subheader("Extracted SOP Section")
#                         st.text_area("SOP Text", sop_text, height=200)
                    
#                     # Compare logs with SOP
#                     st.subheader("Comparison Results")
#                     model_name = model_options[selected_model]
#                     comparison_results = compare_logs_and_sop(sop_text, log_text, model_name)
#                     st.text_area("Comparison Results", comparison_results, height=400)
                
#                 st.success("Processing completed!")
                
#             except Exception as e:
#                 st.error(f"Error processing files: {str(e)}")
#     else:
#         st.info("Please upload both log and SOP files to begin processing.")


# if __name__ == "__main__":
#     main()

def set_custom_css():
    custom_css = """
    <style>
    /* Center the header */
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    /* Style for subheaders */
    .section-header {
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    /* Style for text areas */
    .stTextArea>div>div>textarea {
        font-family: monospace;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="SOP vs Log Comparison",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Apply custom CSS for better formatting
    set_custom_css()
    
    # Main header
    st.markdown("<div class='main-header'>Log Analyzer AI</div>", unsafe_allow_html=True)
    
    # Sidebar inputs with expanders for grouping
    st.sidebar.header("Upload Your Files")
    with st.sidebar.expander("Log File Upload", expanded=True):
        log_file = st.file_uploader("Upload Log File (Excel)", type=["xlsx"], key="log")
    
    with st.sidebar.expander("SOP File Upload", expanded=True):
        sop_file = st.file_uploader("Upload SOP File (PDF)", type=["pdf"], key="sop")
    
    st.sidebar.header("General Settings")
    machine_name = st.sidebar.text_input("Machine Name", "PAM GLATT")
    
    st.sidebar.header("Log Filter Settings")
    start_activity = st.sidebar.text_input("Start Activity", "PAM GLATT started via SCADA. (Status changed from Off to On)")
    end_activity = st.sidebar.text_input("End Activity", "PAM GLATT stopped via SCADA. (Status changed from On to Off)")
    
    st.sidebar.header("SOP Settings")
    section_identifier = st.sidebar.text_input("SOP Section Identifier", "")
    
    model_options = {
        "Llama 3.2": "llama3.2",
        "DeepSeek": "deepseek-r1:7b"
    }
    selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))
    
    st.sidebar.markdown("---")
    submit_button = st.sidebar.button("Process Files")
    
    # Main content area
    st.markdown("## File Processing Overview")
    
    # Check if files have been uploaded
    if not log_file or not sop_file:
        st.info("Please upload both the Log File and the SOP File in the sidebar to begin processing.")
        return

    # Process files when the user clicks the submit button
    if submit_button:
        st.markdown("### Processing Files")
        try:
            with st.spinner('Processing files...'):
                # Read and filter the log file
                df = pd.read_excel(log_file)
                filtered_df = get_rows_between_activities(df, start_activity, end_activity)
                st.success(f"Found {len(filtered_df)} rows between the specified activities.")
                
                # Convert filtered log rows to text format
                log_text = "\n".join(
                    filtered_df.astype(str).apply(lambda x: ' | '.join(x), axis=1)
                )
                
                # Extract the relevant section from the SOP PDF
                sop_text = get_machine_procedure(sop_file, machine_name, section_identifier)
                if not sop_text:
                    st.error("Could not find the specified SOP section. Please verify your settings.")
                    return

                # Display the results in two columns
                st.markdown("#### Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='section-header'>Filtered Log Entries</div>", unsafe_allow_html=True)
                    st.dataframe(filtered_df, use_container_width=True)
                
                with col2:
                    st.markdown("<div class='section-header'>Extracted SOP Section</div>", unsafe_allow_html=True)
                    st.text_area("SOP Text", sop_text, height=250)
                
                # Compare logs with SOP using the selected model
                st.markdown("#### Comparison Results")
                model_name = model_options[selected_model]
                comparison_results = compare_logs_and_sop(sop_text, log_text, model_name)
                st.text_area("Comparison Results", comparison_results, height=400)
            
            st.success("Processing completed successfully!")
            
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
    else:
        st.info("When ready, click 'Process Files' in the sidebar to start.")

if __name__ == "__main__":
    main()
