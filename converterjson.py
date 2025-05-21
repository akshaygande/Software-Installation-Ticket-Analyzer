import pandas as pd
import json
import os

def convert_xlsx_to_json(xlsx_file, json_file, selected_columns=None):
    """
    Convert an XLSX file to JSON, selecting only specific columns.
    
    Parameters:
    - xlsx_file: Path to the input XLSX file
    - json_file: Path where the JSON file will be saved
    - selected_columns: List of column names to include (if None, includes all columns)
    """
    try:
        df = pd.read_excel(xlsx_file)
        
        if selected_columns:
            available_columns = [col for col in selected_columns if col in df.columns]
            if not available_columns:
                print(f"None of the selected columns {selected_columns} exist in the file.")
                print(f"Available columns are: {list(df.columns)}")
                return False
            
            df = df[available_columns]
        
        json_data = df.to_dict(orient='records')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully converted {xlsx_file} to {json_file}")
        print(f"Selected columns: {list(df.columns)}")
        return True
    
    except Exception as e:
        print(f"Error converting file: {e}")
        return False

if __name__ == "__main__":
    input_file = "Genral Data.xlsx" 
    output_file = "Genral Data_short.json"  
    
    # columns_to_include = ["inc_number", "inc_short_description", "inc_escalation", "inc_caller_id", "inc_caller_id.user_name", "inc_caller_id.email", "inc_caller_id.employee_number", "inc_assignment_group", "inc_close_code", "inc_close_notes", "inc_u_classification", "inc_u_service_category", "inc_priority"]
    columns_to_include = ["inc_short_description"]
    
    convert_xlsx_to_json(input_file, output_file, columns_to_include)