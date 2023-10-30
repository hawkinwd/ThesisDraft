import csv
import os

# Get a list of all files in the current directory that end with .txt
txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
totals = []
# Loop through each file in the list
for txt_file in txt_files:
    total = 0
    # Open the file using the csv module
    with open(txt_file, 'r') as file:
        reader = csv.reader(file)
        # Loop through each row in the CSV file
        for row in reader:
            # Add the value in the final column to a running total
            total += int(row[-1])
    # Print the total for each file
    print(f'Total for {txt_file}: {total}')
    totals.append(total)
if len(totals) == 2:
    print("Diff = ", int(totals[0]) - int(totals[1]))
