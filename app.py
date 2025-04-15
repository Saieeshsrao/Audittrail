import streamlit as st
import pandas as pd
from utils import find_machine_rows, get_rows_between_activities
from sop_extractor import get_machine_procedure
from compare_logs_sop import compare_logs_and_sop
import io
import re
import csv


def set_custom_css():
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .section-header {
            font-size: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .stTextArea>div>div>textarea {
            font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)

def markdown_table_to_dataframe(markdown_text):
    # Split the text into lines and remove empty lines
    lines = [line.strip() for line in markdown_text.split('\n') if line.strip()]
    
    if not lines or len(lines) < 3:  # Need at least header, separator, and one data row
        return None
    
    # First line contains headers
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    
    # Skip the separator line (second line with dashes)
    data_rows = []
    for line in lines[2:]:  # Start from third line (after headers and separator)
        if '|' in line:
            # Split the line by | and clean up each cell
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(cells) == len(headers):  # Only add rows that match header count
                data_rows.append(cells)
    
    if data_rows:
        return pd.DataFrame(data_rows, columns=headers)
    return None




def main():
    st.set_page_config(
        page_title="SOP vs Log Comparison",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    set_custom_css()

    st.markdown("<div class='main-header'>Log Analyzer AI</div>", unsafe_allow_html=True)

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

    st.sidebar.markdown("---")
    submit_button = st.sidebar.button("Process Files")

    st.markdown("## File Processing Overview")

    if not log_file or not sop_file:
        st.info("Please upload both the Log File and the SOP File in the sidebar to begin processing.")
        return

    if submit_button:
        st.markdown("### Processing Files")
        try:
            with st.spinner('Processing files...'):
                df = pd.read_excel(log_file)
                filtered_df = get_rows_between_activities(df, start_activity, end_activity)
                st.success(f"Found {len(filtered_df)} rows between the specified activities.")

                # Create structured log text with headers and rows
                headers = filtered_df.columns.tolist()
                log_text = "Headers: " + " | ".join(headers) + "\n"
                log_text += "Rows:\n"
                log_text += "\n".join(
                    filtered_df.astype(str).apply(lambda x: ' | '.join(x), axis=1)
                )

                sop_text = get_machine_procedure(sop_file, machine_name, section_identifier)
                if not sop_text:
                    st.error("Could not find the specified SOP section. Please verify your settings.")
                    return

                st.markdown("#### Results")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("<div class='section-header'>Filtered Log Entries</div>", unsafe_allow_html=True)
                    st.dataframe(filtered_df, use_container_width=True)

                with col2:
                    st.markdown("<div class='section-header'>Extracted SOP Section</div>", unsafe_allow_html=True)
                    st.text_area("SOP Text", sop_text, height=250)

                st.markdown("#### Comparison Results")
                with st.spinner("Analyzing compliance..."):
                    comparison_results = compare_logs_and_sop(sop_text, log_text)

                    # Convert markdown to DataFrame
                    comparison_df = markdown_table_to_dataframe(comparison_results)

                    if comparison_df is not None:
                        # Configure the display settings for better visibility
                        st.markdown("### Detailed Comparison Analysis")
                        
                        # Set up custom styling for the DataFrame
                        st.markdown("""
                        <style>
                        .dataframe-container {
                            margin: 1rem 0;
                            max-width: 100%;
                            overflow-x: auto;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Display the DataFrame with custom settings
                        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                        st.dataframe(
                            comparison_df,
                            use_container_width=True,
                            height=400,  # Adjust this value based on your needs
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Download button
                        csv_buffer = io.StringIO()
                        comparison_df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue().encode("utf-8")
                        st.download_button(
                            label="📥 Download Comparison Results as CSV",
                            data=csv_data,
                            file_name="comparison_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("Could not parse AI response into a table. Displaying raw output below.")
                        st.markdown(f"<pre>{comparison_results}</pre>", unsafe_allow_html=True)

                    with st.expander("View Raw Results"):
                        st.text_area("Raw Analysis Results", comparison_results, height=300)

            st.success("Processing completed successfully!")

        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")

    else:
        st.info("When ready, click 'Process Files' in the sidebar to start.")

if __name__ == "__main__":
    main()
