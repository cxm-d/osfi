# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os


dropdown_values = [
    'Z005', 'Z001', 'AV', 'FG', 'AI', 'FQ', 'AC', 'AE', 'FJ', 'AW', 
    'FZ', 'AA', 'AR', 'AO', 'BG', 'BD', 'FV', 'AM', 'FE', 'AY', 
    'FS', 'BB', 'FM', 'EW', 'AU', 'BE', 'FP', 'FO', 'GA', 'AZ', 
    'EN', 'EQ', 'BF', 'AG', 'FI', 'BH', 'FF', 'BC', 'FR', 'AB', 
    'AS', 'EY', 'AD', 'AT', 'EX', 'AP', 'FX', 'AQ'
]  # Complete list of dropdown values

# Define the list of dates to iterate over
dates_list = ["7 - 2024", "6 - 2024", "5 - 2024", "4 - 2024", "3 - 2024", "2 - 2024", "1 - 2024",
    "12 - 2023", "11 - 2023", "10 - 2023", "9 - 2023", "8 - 2023", "7 - 2023", "6 - 2023", 
    "5 - 2023", "4 - 2023", "3 - 2023", "2 - 2023", "1 - 2023",
    "12 - 2022", "11 - 2022", "10 - 2022", "9 - 2022", "8 - 2022", "7 - 2022", "6 - 2022", 
    "5 - 2022", "4 - 2022", "3 - 2022", "2 - 2022", "1 - 2022",
    "12 - 2021", "11 - 2021", "10 - 2021", "9 - 2021", "8 - 2021", "7 - 2021", "6 - 2021", 
    "5 - 2021", "4 - 2021", "3 - 2021", "2 - 2021", "1 - 2021",
    "12 - 2020", "11 - 2020", "10 - 2020", "9 - 2020", "8 - 2020", "7 - 2020", "6 - 2020", 
    "5 - 2020", "4 - 2020", "3 - 2020", "2 - 2020", "1 - 2020",
    "12 - 2019", "11 - 2019", "10 - 2019", "9 - 2019", "8 - 2019", "7 - 2019", "6 - 2019", 
    "5 - 2019", "4 - 2019", "3 - 2019", "2 - 2019", "1 - 2019"]  

# Base URL for the form
form_url = 'https://ws1ext.osfi-bsif.gc.ca/WebApps/FINDAT/DTIBanks.aspx?T=0&LANG=E'

# Create a session
s = requests.Session()

def get_viewstate_data(soup):
    """Extracts viewstate related data from the soup."""
    return {
        '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'],
        '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'],
        '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'],
    }
# %%
def submit_form(s, viewstate_data, value, date):
    """Submits the form and checks if the response indicates success."""
    data = {
        '__VIEWSTATE': viewstate_data['__VIEWSTATE'],
        '__VIEWSTATEGENERATOR': viewstate_data['__VIEWSTATEGENERATOR'],
        '__EVENTVALIDATION': viewstate_data['__EVENTVALIDATION'],
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionType': 'type1RadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionsDropDownList': value,
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$Frequency': 'monthlyRadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDropDownList': 'DTI-1',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDatesDropDownList': date,
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$submitButton': 'Submit',
    }

    response = s.post(form_url, data=data)

    # Check if the response is valid 
    if 'FinancialData.aspx' in response.text:
        report_id = response.text.split('FinancialData.aspx')[0].rsplit('/', 1)[-1]
        return report_id  # Return report ID if successful
    else:
        return None  # Return None if unsuccessful

def sanitize_filename(text):
    """Remove or replace characters that are not allowed in filenames."""
    return re.sub(r'[^\w\-_\. ]', '_', text)


def process_report(s, report_id, value):
    """Fetches and processes the report data."""
    report_url = f'https://ws1ext.osfi-bsif.gc.ca/WebApps/Temp/{report_id}FinancialData.aspx'
    r = s.get(report_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Extract <p> values
    p_tags = [p.get_text(strip=True) for p in soup.find_all('p')]

    # Extract table data
    table = soup.find('table')  # Adjust selector if necessary
    if table:
        df = pd.read_html(str(table))[0]

        # Add the <p> values as a new column in the DataFrame
        df['P_Tags'] = ', '.join(p_tags)

        # Save the DataFrame to a CSV file
        if len(p_tags) >= 2:
            p1 = sanitize_filename(p_tags[0])
            p2 = sanitize_filename(p_tags[1])
            file_name = f'OSFI_{p1}_{p2}.csv'
        else:
            file_name = 'financial_data_unknown.csv'  

        file_path = os.path.join('osfi_spreadsheets_v2', file_name)
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    else:
        print("No table found on the page.")

# Main loop to process all values and dates
# for value in dropdown_values:
#     print(f"Processing value: {value}")

#     # Get the initial page to fetch VIEWSTATE and other required data
#     r = s.get(form_url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     viewstate_data = get_viewstate_data(soup)
    
#     for date in dates_list:
#         print(f"Checking date: {date} for value: {value}")
#         report_id = submit_form(s, viewstate_data, value, date)
        
#         if report_id:
#             print(f"Success: Processed value {value} and date {date}")
#             process_report(s, report_id, value)
#         else:
#             print(f"Skipping: Date {date} not available for value {value}")

#     print(f"Finished processing value: {value}")


for value in dropdown_values:
    print(f"Processing value: {value}")
    
    for date in dates_list:
        # Get the initial page to fetch VIEWSTATE and other required data for each date
        r = s.get(form_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        viewstate_data = get_viewstate_data(soup)
        
        print(f"Checking date: {date} for value: {value}")
        report_id = submit_form(s, viewstate_data, value, date)
        
        if report_id:
            print(f"Success: Processed value {value} and date {date}")
            process_report(s, report_id, value)
        else:
            print(f"Skipping: Date {date} not available for value {value}")
    
    print(f"Finished processing value: {value}")