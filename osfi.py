import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define your dropdown values
dropdown_values = [
    'Z005', 'Z001', 'AV', 'FG', 'AI', 'FQ', 'AC', 'AE', 'FJ', 'AW', 
    'FZ', 'AA', 'AR', 'AO', 'BG', 'BD', 'FV', 'AM', 'FE', 'AY', 
    'FS', 'BB', 'FM', 'EW', 'AU', 'BE', 'FP', 'FO', 'GA', 'AZ', 
    'EN', 'EQ', 'BF', 'AG', 'FI', 'BH', 'FF', 'BC', 'FR', 'AB', 
    'AS', 'EY', 'AD', 'AT', 'EX', 'AP', 'FX', 'AQ'
]  # Complete list of dropdown values

# Base URL for the form
form_url = 'https://ws1ext.osfi-bsif.gc.ca/WebApps/FINDAT/DTIBanks.aspx?T=0&LANG=E'

# Create a session
s = requests.Session()

# Loop through each dropdown value
for value in dropdown_values:
    # Get the initial page to fetch VIEWSTATE and other required data
    r = s.get(form_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Prepare the POST data
    data = {
        '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'],
        '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'],
        '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'],
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionType': 'type1RadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$institutionTypeCriteria$institutionsDropDownList': value,
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$Frequency': 'monthlyRadioButton',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDropDownList': 'DTI-1',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$dtiReportCriteria$monthlyDatesDropDownList': '4 - 2020',
        'DTIWebPartManager$gwpDTIBankControl1$DTIBankControl1$submitButton': 'Submit',
    }

    # Submit the form with the selected value
    r = s.post(form_url, data=data)

    # Extract the report ID from the response
    report_id = r.text.split('FinancialData.aspx')[0].rsplit('/', 1)[-1]

    # Fetch the report data
    report_url = f'https://ws1ext.osfi-bsif.gc.ca/WebApps/Temp/{report_id}FinancialData.aspx'
    r = s.get(report_url)

    # Parse the report data
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Extract <p> values
    p_tags = [p.get_text(strip=True) for p in soup.find_all('p')]

    # Extract table data
    table = soup.find('table')  # Adjust selector if necessary
    if table:
        df = pd.read_html(str(table))[0]

        # Add the <p> values as a new column in the DataFrame
        df['P_Tags'] = ', '.join(p_tags)  # Join the <p> tags into a single string

        # Add a column for the dropdown value
        #df['DropdownValue'] = value  

        # Save each DataFrame to a separate CSV file
        file_name = f'financial_data_{value}.csv'
        df.to_csv(file_name, index=False)