#!/opt/anaconda3/bin/python

import os
import gspread
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
load_dotenv()

import google.auth
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive.readonly']

def get_gspread_client():
    """ Authenticate using a service account. """

    creds, _ = google.auth.default(scopes=SCOPES)

    return gspread.authorize(creds)

def get_links_from_sheet(sheet_name):
    """Retrieve two lists of stock from the inventory spreadsheet."""
    client = get_gspread_client()
    sheet = client.open(sheet_name).sheet1
    items_to_order = []
    wholesale_list = []

    names, sellers, links, quantities = (
    sheet.col_values(2),
    sheet.col_values(3),
    sheet.col_values(4),
    sheet.col_values(5)
)
    for i in range(1, len(quantities)):
        if quantities[i].strip().isdigit() and int(quantities[i]) > 0:
            if sellers[i] == "WHOLESALE":
                wholesale_list.append(quantities[i] + " of " + names[i])
            else:
                items_to_order.append(quantities[i] + " of " + names[i]
                                    + ", link: " + links[i])
            
    return items_to_order, wholesale_list

def send_email(items_to_order, wholesale_list, recipient):
    """Send the stock list by email."""
    sender = os.getenv('SENDER')
    password = os.getenv('APP_PASSWORD') 

    subject = f"Weekly Inventory Order List - {datetime.now().strftime('%Y-%m-%d')}"
    body = (
        "Here are the links to buy the items needed:\n\n"
        + "\n".join(items_to_order)
        + "\n\nAnd here is a shopping list for the wholesaler:\n\n"
        + "\n".join(wholesale_list)
    )

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def main():
    items_to_order, wholesale_list = get_links_from_sheet(os.getenv('SHEET_NAME'))
    if items_to_order or wholesale_list:
        send_email(items_to_order, wholesale_list, os.getenv('RECIPIENT'))
    else:
        print("No items to order this week.")

if __name__ == "__main__":
    main()
    