#!/opt/anaconda3/bin/python


import gspread
from google.oauth2 import service_account

from google.auth.transport.requests import Request
import os
from dotenv import load_dotenv
import pickle
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
load_dotenv()


# Define the scope for Sheets + Drive
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive.readonly']

def get_gspread_client():
    """
    Authenticate using a service account. 
    """
    service_account_path = os.getenv('gcpkey_path')
    creds = service_account.Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)

# Get item links from the sheet
def get_links_from_sheet(sheet_name):
    client = get_gspread_client()
    sheet = client.open(sheet_name).sheet1
    items_to_order = []
    names, links, quantities = sheet.col_values(2), sheet.col_values(4), sheet.col_values(5)
    for i in range(1, len(quantities)):
        if quantities[i].strip().isdigit() and int(quantities[i]) > 0:
            items_to_order.append(quantities[i] + " of " + names[i]
                                   + ", link: " + links[i])
            
    return items_to_order

# Email the links
def send_email(items_to_order, recipient):
    sender = os.getenv('sender')
    password = os.getenv('app_password') # Use an app password if using Gmail 2FA

    subject = f"Weekly Inventory Order List - {datetime.now().strftime('%Y-%m-%d')}"
    body = "Here are the links to buy the items needed:\n\n" + "\n".join(items_to_order)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def main():
    items_to_order = get_links_from_sheet(os.getenv('sheet_name'))
    if items_to_order:
        send_email(items_to_order, os.getenv('recipient'))
    else:
        print("No items to order this week.")

if __name__ == "__main__":
    main()
    