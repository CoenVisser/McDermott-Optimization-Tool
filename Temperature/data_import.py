import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Read the CSV file
csv_path = 'Temperature/temp_data_csv.csv'
df = pd.read_csv(csv_path)

# Select the columns you want
selected_columns = df[['Start time UTC', 'Temperature in Oulu - real time data']]

# Convert the DataFrame to a numpy array
temp_array = selected_columns.values

temp_array_daily_rows = temp_array[:,1].reshape(-1, 480)

min_temps = np.amin(temp_array_daily_rows, axis=1)
min_temps = np.array(min_temps, dtype=float)

mean_temps = np.mean(temp_array_daily_rows, axis=1)
mean_temps = np.array(mean_temps, dtype=float)

max_temps = np.amax(temp_array_daily_rows, axis=1)
max_temps = np.array(max_temps, dtype=float)

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def quarter(date):
    year = date.year
    quarter = (date.month-1)//3 + 1
    return f'Q{quarter} {year}'

window_size = 15  # Change this to the desired window size

# Apply the moving average to your data
min_temps_smooth = moving_average(min_temps, window_size)
mean_temps_smooth = moving_average(mean_temps, window_size)
max_temps_smooth = moving_average(max_temps, window_size)

# Adjust the days to match the length of the smoothed data
days_smooth = range(len(min_temps_smooth))

# Create a date range starting from 1st Feb 2015
start_date = '2015-02-01'
end_date = pd.date_range(start=start_date, periods=len(min_temps_smooth))


# Plot the smoothed temperatures
plt.figure(figsize=(10,6))
plt.ylim(-20, 35)

plt.plot(end_date, mean_temps_smooth, label='Mean Temperatures', color='black')

# Highlight the sections where the max temperature is higher than 3
plt.fill_between(end_date, 3, 50, where=mean_temps_smooth>3, color='orange', alpha=0.5, label='Possible to Pour Concrete')

# Fill the area between the mean and max temperatures
plt.fill_between(end_date, mean_temps_smooth, max_temps_smooth, where=max_temps_smooth>=mean_temps_smooth, color='red', alpha=0.5, label='Up to Maximum Temperatures')

# Fill the area between the min and mean temperatures
plt.fill_between(end_date, min_temps_smooth, mean_temps_smooth, where=min_temps_smooth<=mean_temps_smooth, color='blue', alpha=0.5, label='Down to Minimum Temperatures')

# Add a horizontal line at y=3
plt.axhline(y=3, color='green', linestyle='--', label='Minimum Concrete Pouring Temperature', linewidth=3)

# Set the x-axis to show quarters
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # to get a tick every 3 months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # format the date as quarter
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: quarter(mdates.num2date(x))))

# Set the x-axis limits
ax.set_xlim([pd.to_datetime(start_date), end_date[-1]])

# Add labels and a legend
plt.xlabel('Date')
plt.ylabel('Temperature')
plt.title('Daily Temperature Data')
plt.legend()

# Display the plot
plt.show()