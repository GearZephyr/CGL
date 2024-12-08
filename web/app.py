import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import os

# Function to check and store valid sequences based on user input
def get_valid_sequence(df, start_index, diff, recurrence):
    sequence = []
    
    # Check if 'ROLL' exists
    if 'ROLL' not in df.columns:
        st.error("Column 'ROLL' not found in the DataFrame")
        return []
    
    sequence = [df.loc[start_index, 'ROLL']]
    
    # Loop through the following rows to build the sequence
    for i in range(start_index + 1, len(df)):
        current_number = df.loc[i, 'ROLL']
        prev_number = df.loc[i - 1, 'ROLL']
        
        # If the difference between current and previous number is <= diff, add to sequence
        if abs(current_number - prev_number) <= diff:
            sequence.append(current_number)
        else:
            break  # Stop when the difference exceeds the allowed value
    
    # Only return the sequence if it has at least 'recurrence' numbers
    if len(sequence) >= recurrence:
        return sequence
    return []

# Streamlit UI
st.title('Data Processing with ROLL Sequences')

# Get difference and recurrence from user
difference = st.number_input('enter min. difference between roll number:', min_value=1, value=4)
recurrence = st.number_input('Enter minimum set to be grouped :', min_value=1, value=9)

# Specify file path to the CSV file in the 'data' folder
file_path = os.path.join('data', 'data.csv')

if os.path.exists(file_path):
    # Display the button to process the data
    if st.button('Process Data'):
        try:
            # Display loading spinner while processing
            with st.spinner('Processing data, please wait...'):
                # Read the CSV file
                df = pd.read_csv(file_path)
                df.columns = df.columns.str.strip()  # Clean column names
                
                # Display columns for the user to inspect
                all_filtered_rows = []
                group_id = 0  # Variable to assign different colors for each group

                # Loop through the rows of the DataFrame
                i = 0
                while i < len(df):
                    # Get a valid sequence starting from this row
                    valid_sequence = get_valid_sequence(df, i, difference, recurrence)
                    
                    # If a valid sequence is found, add corresponding rows to the filtered list
                    if valid_sequence:
                        # Add rows to the filtered list with a group ID
                        for num in valid_sequence:
                            row_index = df[df['ROLL'] == num].index[0]
                            row = df.loc[row_index].copy()
                            row['Group'] = group_id  # Add a group identifier
                            all_filtered_rows.append(row)
                        
                        # Increment group ID for the next group
                        group_id += 1
                        
                        # Skip to the last row of the found sequence
                        i = df[df['ROLL'] == valid_sequence[-1]].index[0] + 1
                    else:
                        # Move to the next row if no valid sequence is found
                        i += 1

                # Convert all filtered rows to a DataFrame
                final_df = pd.DataFrame(all_filtered_rows, columns=df.columns.tolist() + ['Group'])
                
                # Apply alternating colors for each set (group)
                def highlight_groups(row):
                    color = 'lightblue' if row['Group'] % 2 == 0 else 'lightgreen'
                    return [f'background-color: {color}' for _ in row]

                # Apply the highlight function to all rows
                styled_df = final_df.style.apply(highlight_groups, axis=1)

                # Show the styled DataFrame
                st.subheader("Processed Data with Group Colors")
                st.dataframe(styled_df)

                # Function to convert DataFrame to Excel
                def to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    return output.getvalue()

                # Create Excel file and download link
                excel_data = to_excel(final_df)
                st.download_button(
                    label="Download Processed Data",
                    data=excel_data,
                    file_name="processed_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Show total number of valid rows (people)
                st.write(f"Total number of valid rows (people) in the output: {len(final_df)}")

        except Exception as e:
            st.error(f"Error reading file: {e}")
else:
    st.error(f"The file 'data.csv' was not found in the 'data' folder.")
