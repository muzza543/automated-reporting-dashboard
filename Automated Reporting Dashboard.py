from faker import Faker
import pandas as pd
import random
from datetime import timedelta
import os

'''Create fake data to use for the automated reporting dashboard using the Faker Library whilst Panda will be used to export the data to a CSV file'''

fake = Faker() #create an instance of the Faker class 
data = [] #python list of dictionaries hence 1 dictionary equivalent to 1 ticket
count = 500 #number of tickets to generate


'''Issue priority map to automatically set the priority of the issue based on the issue type'''
issue_priority_map = {
    "Network": "High",
    "Login": "Medium",
    "Hardware": "High",
    "Software": "Low"
}

print("Generating tickets...")

for i in range(count): #500 rows of data

    issue_type = random.choice(["Login", "Network", "Hardware", "Software"]) #randomly picks an issue type from the list
    priority = issue_priority_map[issue_type] #sets the priority of the issue based on the issue type using the priority map
    date_opened = fake.date_time_this_year() #random date and time this year
    status = random.choice(["Open","Closed", "In Progress"]) #randomly picks a status from the list

    '''If the status is closed, it can then pick a date closed which correlates with the resolution hours. 
It would make no sense if the date closed was for example before the date opened or the reoslution hours and date closed weren't relating to each other. 
So this if conditional statement just makes everything make sense. '''

    if status == "Closed":
        resolution_hours = random.randint(1,72) #hours
        date_closed = date_opened + timedelta(hours = resolution_hours)

    else:
        resolution_hours = None
        date_closed = None


    '''Add the data to the list as a dictionary - each dictionary is a ticket. Iterates 500 times due to the count variable'''
    data.append({
        "ticket_id": i+1, #incrementing count by 1 each time for ticket_id
        "client":fake.company(), #fake client company name
        "issue_type": issue_type,
        "priority": priority,
        "date_opened":date_opened,
        "resolution_time": resolution_hours, #hours
        "date_closed": date_closed,
        "status": status,
        
        })


df = pd.DataFrame(data) #converts the list of the dictionaries to pandas dataframe to export to a CSV file


print(f"Calculating KPIs...") 


'''KPI Calculations to display on the dashboard'''
total_tickets = len(df) #total number of tickets generated
open_tickets = len(df[df['status'] == 'Open']) #number of open tickets
closed_tickets = len(df[df['status'] == 'Closed']) #number of closed tickets
current_tickets = len(df[df['status'] == 'In Progress']) #number of tickets in progress

#Average resolution time for the closed tickets
closed_tickets_df = df[df['status'] == 'Closed'] #dataframe of closed tickets only
avg_resolution_time = closed_tickets_df['resolution_time'].mean() if len(closed_tickets_df) > 0 else 0 #this generates the average resolution time for closed tickets. if no closed tickets, it will return 0

#SLA Compliance - the percentage of tickets being resolved within 24 hours
sla_threshold = 24 #limit in hours
compliant_tickets = len(closed_tickets_df[closed_tickets_df['resolution_time'] <= sla_threshold]) #number of tickets resolved within the SLA threshold
sla_compliance = (compliant_tickets / len(closed_tickets_df)) * 100 if len(closed_tickets_df) > 0 else 0 #percentage of tickets resolved within the SLA threshold. if there are no closed tickets, it will return 0


# Create KPI summary
kpi_data = { # dictionary for the KPI data
    'Metric': ['Total Tickets', 
               'Open Tickets', 
               'Closed Tickets', 
               'In Progress Tickets', 
               'Average Resolution Time (hrs)', 
               'SLA Compliance (%)'
    ],
    'Value': [total_tickets, #list of values for each metric
              open_tickets, 
              closed_tickets, 
              current_tickets, 
              round(avg_resolution_time, 2), #rounding to 2 decimal places 
              round(sla_compliance, 2) #rounding to 2 decimal places

    ]
}

kpi_df = pd.DataFrame(kpi_data) #converts the KPI dictionary to a pandas dataframe

# Create daily ticket summary for trends
df['date_opened_only'] = pd.to_datetime(df['date_opened']).dt.date
daily_opened = df.groupby('date_opened_only').size().reset_index(name='tickets_opened')

# For closed tickets daily
closed_with_dates = df[df['date_closed'].notna()].copy()
closed_with_dates['date_closed_only'] = pd.to_datetime(closed_with_dates['date_closed']).dt.date
daily_closed = closed_with_dates.groupby('date_closed_only').size().reset_index(name='tickets_closed')

# Merge daily data safely to ensure all the dates are captured
daily_summary = pd.merge(
    daily_opened, daily_closed, 
    left_on='date_opened_only', right_on='date_closed_only', 
    how='outer'
)

# Create a single date column
daily_summary['date'] = daily_summary['date_opened_only'].combine_first(daily_summary['date_closed_only']) #combine the two date columsn into one

# Drop the old separate date columns
daily_summary = daily_summary[['date', 'tickets_opened', 'tickets_closed']] #keep only the relevant columns

# Replace NaNs with 0 for ticket counts only
daily_summary[['tickets_opened', 'tickets_closed']] = daily_summary[['tickets_opened', 'tickets_closed']].fillna(0) #fill NaN values with 0 for ticket counts
# Ensure correct types
daily_summary['date'] = pd.to_datetime(daily_summary['date']) #convert to datetime
daily_summary = daily_summary.sort_values('date') #sort by date

daily_summary['year'] = daily_summary['date'].dt.year
daily_summary['month'] = daily_summary['date'].dt.month
daily_summary['month_name'] = daily_summary['date'].dt.strftime('%B') #full month name
daily_summary['week'] = daily_summary['date'].dt.isocalendar().week #week number of the year
daily_summary['day'] = daily_summary['date'].dt.day #day of the month


# Issue type distribution
issue_distribution = df['issue_type'].value_counts().reset_index() #count of each issue type
issue_distribution.columns = ['issue_type', 'count'] #to rename the columns
issue_distribution['percentage'] = (issue_distribution['count'] / total_tickets) * 100 #percentage of each issue type

# Priority distribution  
priority_distribution = df['priority'].value_counts().reset_index()
priority_distribution.columns = ['priority', 'count']
priority_distribution['percentage'] = (priority_distribution['count'] / total_tickets) * 100

sla_threshold = 24
df['within_sla'] = df['resolution_time'].apply(lambda x: 1 if x is not None and x <= sla_threshold else 0) #this creates a new column called within_sla which is 1 if the resolution time is within the SLA threshold and 0 otherwise

# Save all files
print("\nSaving files...")

excel_file = "tickets_tracking.xlsx"
'''This code saves all the dataframes into a single excel file using multiple sheets. Utilises pandas.Excelwriter function with the openpyxl engine. This hence means its best to keep it to only open as on excel and remove options to open in different applications '''

with pd.ExcelWriter(excel_file, engine = "openpyxl") as writer: #using openpyxl engine to write to excel
    df.to_excel(writer, sheet_name = "Tickets", index = False) #all tickets data
    kpi_df.to_excel(writer, sheet_name = "KPI Summary", index = False) #KPI summary data
    daily_summary.to_excel(writer, sheet_name = "Daily Ticket Trends", index = False) #daily ticket trends data
    issue_distribution.to_excel(writer, sheet_name = "Issue Type Distribution", index = False) #issue type distribution data
    priority_distribution.to_excel(writer, sheet_name = "Priority Distribution", index = False) #priority distribution data

#Save all the files 
print(f"\nAll files saved successfully into {excel_file}.")



'''Allows the user to choose how to open the CSV file'''

print("\nChoose your option:")
print("1 - Excel")
print("2 - Don't open the file")

choice = input("Enter 1 or 2:")

if choice == "1":
    os.startfile(excel_file) #opens the excel file using the default application

elif choice == "2":
    print(f"You do not wish to open the file {excel_file}. Saved but not opened")

else:
    print("Invalid choice. CSV saved but not opened")

print("\nAll operations completed.")
