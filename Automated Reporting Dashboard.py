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
csv_file = "tickets.csv" #name of the CSV file
df.to_csv(csv_file, index=False) #exports panda's dataframe to a CSV file whilst index = False means it won't add an extra column to index as ticket_id already does that
print(f"{csv_file} saved.") #confirmation messages


'''Allows the user to choose how to open the CSV file'''

print("\nChoose how to open the CSV:")
print("1 - Excel")
print("2 - Notepad")
print("3 - Pandas(Python library)")
print("4 - Don't open the file")

choice = input("Enter 1, 2, 3 or 4:")

if choice == "1":
    os.startfile(csv_file) #opens the CSV file using the operating system's default program for CSV files

elif choice == "2":
    os.system(f"notepad {csv_file}") #opens the CSV file using the operating system's notepad

elif choice == "3":
    df_loaded = pd.read_csv(csv_file) #loads the CSV file into a pandas dataframe
    print(df_loaded.head(10)) #prints the first 10 rows of the dataframe

elif choice == "4":
    print(f"You do not wish to open the file {csv_file}. Saved but not opened")

else:
    print("Invalid choice. CSV saved but not opened")

