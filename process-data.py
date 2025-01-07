import os

# Define the input file name
input_filename = 'coords.txt'  # Replace with your actual file name if different

# Read the raw data from the text file
with open(input_filename, 'r') as file:
    lines = file.readlines()

# Initialize variables
current_section = None
current_pipeline_name = None
current_data = []
pipelines = {}  # Dictionary to store pipelines and their data
powerlines = {}  # Dictionary to store powerlines and their data

# Process each line
for line in lines:
    line = line.strip()
    if line == "PIPELINES":
        current_section = 'PIPELINES'
    elif line == "POWERLINES":
        current_section = 'POWERLINES'
    elif line.startswith('*'):
        # Save the previous pipeline or powerline data if any
        if current_pipeline_name and current_data:
            if current_section == 'PIPELINES':
                pipelines[current_pipeline_name] = current_data
            elif current_section == 'POWERLINES':
                powerlines[current_pipeline_name] = current_data
            current_data = []
        # Get the new pipeline or powerline name
        current_pipeline_name = line.strip('*').strip()
    elif line:
        # Process the coordinate line
        parts = line.split()
        if len(parts) == 2:
            try:
                # Convert latitude and longitude to float
                latitude = float(parts[0])
                longitude = float(parts[1])
                # Append as (longitude, latitude) to match the desired output
                current_data.append((latitude, longitude))
            except ValueError:
                # Handle the case where conversion to float fails
                pass

# Save the last pipeline or powerline data
if current_pipeline_name and current_data:
    if current_section == 'PIPELINES':
        pipelines[current_pipeline_name] = current_data
    elif current_section == 'POWERLINES':
        powerlines[current_pipeline_name] = current_data

# Create directories if they do not exist
os.makedirs('pipelines', exist_ok=True)
os.makedirs('powerlines', exist_ok=True)

# Write pipeline data to CSV files in the 'pipelines' folder
for pipeline_name, data in pipelines.items():
    # Replace any characters that are invalid in filenames
    safe_pipeline_name = pipeline_name.replace('/', '_').replace('\\', '_').replace(' ', '-').strip()
    filename = os.path.join('pipelines', f"{safe_pipeline_name}.csv")
    with open(filename, 'w') as f:
        f.write(f"{pipeline_name}\n")
        for longitude, latitude in data:
            f.write(f"{longitude},{latitude}\n")

# Write powerline data to CSV files in the 'powerlines' folder
for powerline_name, data in powerlines.items():
    # Replace any characters that are invalid in filenames
    safe_powerline_name = powerline_name.replace('/', '_').replace('\\', '_').replace(' ', '-').strip()
    filename = os.path.join('powerlines', f"{safe_powerline_name}.csv")
    with open(filename, 'w') as f:
        f.write(f"{powerline_name}\n")
        for longitude, latitude in data:
            f.write(f"{longitude},{latitude}\n")

# Print a message when done
print("CSV files have been created for each pipeline and powerline in their respective folders.")
