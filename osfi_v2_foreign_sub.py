# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os



dropdown_values = ['Z002']

# dropdown_values = ['Z005', 'Z002', 'EO', 'DO', 'CD', 'DV', 'ET', 'CA', 'EV', 'CH', 'CC',
#   'ER', 'CJ', 'EZ', 'CV', 'FD', 'CZ', 'EP', 'FY', 'FL', 'CU', 'FA', 'DQ', 'DA', 'FB', 'EJ', 'CI', 'CN', 'DD', 'DE', 'FC',
#   'DF', 'CB', 'FH', 'ES', 'DG', 'CL', 'DH', 'CY', 'CP', 'CK', 'DX', 'EG', 'DZ', 'DB', 'EA', 'DK', 'CR', 'ED', 'EE', 'CF',
#    'DJ', 'DU', 'FK', 'DL', 'EL', 'EK', 'EU', 'CG', 'EH', 'CT', 'EM']

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

# dates_list = ["1 - 2024"]

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
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionType': 'type2RadioButton',
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

    # Extract all table data
    tables = pd.read_html(str(soup))  # Extract all tables as a list of DataFrames


    if len(tables) >= 2:
        # Combine the two tables into one
        # df_combined = pd.concat([tables[0], tables[1]], ignore_index=True)
        df_combined = pd.concat([d.T.reset_index().T for d in [tables[0], tables[1]]])
        # Add the <p> values as a new column in the combined DataFrame
        df_combined['P_Tags'] = ', '.join(p_tags)

        # Save the combined DataFrame to a CSV file
        if len(p_tags) >= 2:
            p1 = sanitize_filename(p_tags[0])
            p2 = sanitize_filename(p_tags[1])
            file_name = f'OSFI_{p1}_{p2}.csv'
        else:
            file_name = 'financial_data_unknown_combined.csv'

        file_path = os.path.join('osfi_spreadsheets_foreign_subs', file_name)
        df_combined.to_csv(file_path, index=False)
        print(f"Combined data saved to {file_path}")
    else:
        print("Less than 2 tables found on the page.")



def simulate_dropdown_selection(s, viewstate_data, value):
    """Simulates selecting a dropdown item to trigger a postback and get updated viewstate."""
    data = {
        '__VIEWSTATE': viewstate_data['__VIEWSTATE'],
        '__VIEWSTATEGENERATOR': viewstate_data['__VIEWSTATEGENERATOR'],
        '__EVENTVALIDATION': viewstate_data['__EVENTVALIDATION'],
        '__EVENTTARGET': 'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionsDropDownList',
        '__EVENTARGUMENT': '',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionType': 'type2RadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionsDropDownList': value,
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$Frequency': 'monthlyRadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDropDownList': 'DTI-1'
    }

    # This simulates selecting the dropdown value and triggering the postback.
    # We need this so that the updated viewstate data can be extracted.
    response = s.post(form_url, data=data)
    return response


for value in dropdown_values:
    print(f"Processing value: {value}")
    
    # Get the initial page to fetch VIEWSTATE and other required data for each dropdown value
    r = s.get(form_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    viewstate_data = get_viewstate_data(soup)
    print(viewstate_data)
    
    # Simulate the dropdown selection for this value
    print(f"Simulating dropdown selection for value: {value}")
    r = simulate_dropdown_selection(s, viewstate_data, value)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Extract updated VIEWSTATE and EVENTVALIDATION after the dropdown interaction
    viewstate_data = get_viewstate_data(soup)
    
    # Now submit the form for each date
    for date in dates_list:
        print(f"Checking date: {date} for value: {value}")

        # Submit the form with the current value and date
        report_id = submit_form(s, viewstate_data, value, date)
        
        if report_id:
            print(f"Success: Processed value {value} and date {date}")
            process_report(s, report_id, value)
        else:
            print(f"Skipping: Date {date} not available for value {value}")
    
    print(f"Finished processing value: {value}")