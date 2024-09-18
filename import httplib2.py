# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define your dropdown values
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
    "5 - 2019", "4 - 2019", "3 - 2019", "2 - 2019", "1 - 2019",
    "12 - 2018", "11 - 2018", "10 - 2018", "9 - 2018", "8 - 2018", "7 - 2018", "6 - 2018", 
    "5 - 2018", "4 - 2018", "3 - 2018", "2 - 2018", "1 - 2018",
    "12 - 2017", "11 - 2017", "10 - 2017", "9 - 2017", "8 - 2017", "7 - 2017", "6 - 2017", 
    "5 - 2017", "4 - 2017", "3 - 2017", "2 - 2017", "1 - 2017",
    "12 - 2016", "11 - 2016", "10 - 2016", "9 - 2016", "8 - 2016", "7 - 2016", "6 - 2016", 
    "5 - 2016", "4 - 2016", "3 - 2016", "2 - 2016", "1 - 2016",
    "12 - 2015", "11 - 2015", "10 - 2015", "9 - 2015", "8 - 2015", "7 - 2015", "6 - 2015", 
    "5 - 2015", "4 - 2015", "3 - 2015", "2 - 2015", "1 - 2015",
    "12 - 2014", "11 - 2014", "10 - 2014", "9 - 2014", "8 - 2014", "7 - 2014", "6 - 2014", 
    "5 - 2014", "4 - 2014", "3 - 2014", "2 - 2014", "1 - 2014",
    "12 - 2013", "11 - 2013", "10 - 2013", "9 - 2013", "8 - 2013", "7 - 2013", "6 - 2013", 
    "5 - 2013", "4 - 2013", "3 - 2013", "2 - 2013", "1 - 2013",
    "12 - 2012", "11 - 2012", "10 - 2012", "9 - 2012", "8 - 2012", "7 - 2012", "6 - 2012", 
    "5 - 2012", "4 - 2012", "3 - 2012", "2 - 2012", "1 - 2012",
    "12 - 2011", "11 - 2011", "10 - 2011", "9 - 2011", "8 - 2011", "7 - 2011", "6 - 2011", 
    "5 - 2011", "4 - 2011", "3 - 2011", "2 - 2011", "1 - 2011",
    "12 - 2010", "11 - 2010", "10 - 2010", "9 - 2010", "8 - 2010", "7 - 2010", "6 - 2010", 
    "5 - 2010", "4 - 2010", "3 - 2010", "2 - 2010", "1 - 2010"]  

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

    # Check if the response is valid (customize this logic as needed)
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
        file_name = 'financial_data_unknown.csv'  # Fallback if not enough <p> tags

    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

# Main logic
for value in dropdown_values:
    print(f"Processing value: {value}")
    # Get the initial page to fetch VIEWSTATE and other required data
    r = s.get(form_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    viewstate_data = get_viewstate_data(soup)
    
    for date in dates_list:
        print(f"Checking date: {date} for value: {value}")
        report_id = submit_form(s, viewstate_data, value, date)
        
        if report_id:
            print(f"Success: Processed value {value} and date {date}")
            process_report(s, report_id, value)
        else:
            print(f"Skipping: Date {date} not available for value {value}")

    print(f"Finished processing value: {value}")
