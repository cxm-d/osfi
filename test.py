import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define your institution dropdown values
institution_dropdown_values = [
    'Z005', 'Z001', 'AV', 'FG', 'AI', 'FQ', 'AC', 'AE', 'FJ', 'AW', 
    'FZ', 'AA', 'AR', 'AO', 'BG', 'BD', 'FV', 'AM', 'FE', 'AY', 
    'FS', 'BB', 'FM', 'EW', 'AU', 'BE', 'FP', 'FO', 'GA', 'AZ', 
    'EN', 'EQ', 'BF', 'AG', 'FI', 'BH', 'FF', 'BC', 'FR', 'AB', 
    'AS', 'EY', 'AD', 'AT', 'EX', 'AP', 'FX', 'AQ'
] 

# Define your date dropdown values
date_dropdown_values = [
    "6 - 2024", "5 - 2024", "4 - 2024", "3 - 2024", "2 - 2024", "1 - 2024",
    "12 - 2023", "11 - 2023", "10 - 2023", "9 - 2023", "8 - 2023", "7 - 2023", 
    "6 - 2023", "5 - 2023", "4 - 2023", "3 - 2023", "2 - 2023", "1 - 2023",
    # Add more as needed...
]

# Base URL for the form
form_url = 'https://ws1ext.osfi-bsif.gc.ca/WebApps/FINDAT/DTIBanks.aspx?T=0&LANG=E'

# Create a session
s = requests.Session()

# Loop through each institution and date dropdown value
for institution_value in institution_dropdown_values:
    for date_value in date_dropdown_values:
        try:
            # Get the initial page to fetch VIEWSTATE and other required data
            r = s.get(form_url)
            soup = BeautifulSoup(r.content, 'html.parser')

            # Prepare the POST data
            data = {
                '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'],
                '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'],
                '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'],
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionType': 'type1RadioButton',
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionsDropDownList': institution_value,
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$Frequency': 'monthlyRadioButton',
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDropDownList': 'DTI-1',
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDatesDropDownList': date_value,
                'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$submitButton': 'Submit',
            }

            # Submit the form with the selected institution and date value
            r = s.post(form_url, data=data)
            
            # Check if the response indicates a missing report or an error
            if "No data found" in r.text or "error" in r.text.lower():
                print(f"No data found for {institution_value} on {date_value}")
                continue

            # Extract the report ID from the response
            report_id = r.text.split('FinancialData.aspx')[0].rsplit('/', 1)[-1]
            report_url = f'https://ws1ext.osfi-bsif.gc.ca/WebApps/Temp/{report_id}FinancialData.aspx'

            # Fetch the report data
            r = s.get(report_url)
            soup = BeautifulSoup(r.content, 'html.parser')

            # Extract <p> values
            p_tags = list(set([p.get_text(strip=True) for p in soup.find_all('p')]))

            # Ensure we have at least two <p> tags for the bank name and date
            if len(p_tags) >= 2:
                # Assume second <p> is the bank name and first is the date
                bank_name = p_tags[1]
                date_text = p_tags[0]
            else:
                # Fallback default values
                bank_name = 'Unknown_Bank'
                date_text = 'Unknown_Date'

            # Clean the strings for the filename (replace spaces, remove special characters)
            bank_name_clean = bank_name.replace(" ", "_").replace(",", "").replace("'", "")
            date_text_clean = date_text.replace(" ", "_").replace(",", "").replace("'", "")

            # Create the file name
            file_name = f'{bank_name_clean}_{date_text_clean}.csv'

            # Extract all tables
            tables = pd.read_html(str(soup))  # This will return a list of DataFrames

            # Check if there are tables present
            if tables:
                # Concatenate all tables into a single DataFrame
                df = pd.concat(tables, ignore_index=True)

                # Add the <p> values as a new column in the DataFrame
                df['P_Tags'] = ', '.join(p_tags)  # Join the <p> tags into a single string

                # Save the DataFrame to a CSV file with the formatted file name
                df.to_csv(file_name, index=False)

                print(f"Data saved to {file_name}")
            else:
                print(f"No tables found for {institution_value} on {date_value}")

        except Exception as e:
            print(f"An error occurred for {institution_value} on {date_value}: {e}")