import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

RESULTS_INPUT = 'results.csv'
ACTUAL_INPUT = 'actual.xlsx'

# Reads in the files and parses out only the useful columns
actual = pd.read_excel(ACTUAL_INPUT)
predicted = pd.read_csv(RESULTS_INPUT)
actual = actual[['full name', 'Right', 'Left']]
actual = actual.rename(index=str, columns={"Right": "actual_right",
                                           "Left": "actual_left"})
predicted = predicted.rename(index=str, columns={"right_wing (mm)":
                                                 "predicted_right",
                                                 "left_wing (mm)":
                                                 "predicted_left"})

# Merging them together and creating new columns for the difference
both = pd.merge(actual, predicted, left_on='full name',
                right_on='image_id').drop(['image_id'], axis=1)
both['left_diff'] = both['predicted_left'] - both['actual_left']
both['right_diff'] = both['predicted_right'] - both['actual_right']
all_diffs = both['right_diff'].append(both['left_diff'])

# Outliers
mean = np.mean(all_diffs)
sd = np.std(all_diffs)
lower = mean - 2 * sd
upper = mean + 2 * sd
print(f"Mean: {mean} SD: {sd}.")
print(f"Lower: {lower} Upper: {upper}.")

outliers = all_diffs[(all_diffs < lower) | (all_diffs > upper)]
print(f"Num outliers: {len(outliers)}")
all_diffs = all_diffs[(all_diffs > lower) & (all_diffs < upper)]

fig, ax = plt.subplots(figsize=(10, 5))
ax = all_diffs.hist(bins='auto')

# Saving the plot
filename = 'result_plot.png'
output_path = os.path.normpath(filename)
plt.xlabel('Difference between (predicted - actual) in mm')
start, end = ax.get_xlim()
plt.ylabel('Number of samples')
plt.title('Error in predicted length')
plt.savefig(output_path)
plt.close()

# Printing the outliers
both['left_SD'] = (both['left_diff'] - mean) / sd
both['right_SD'] = (both['right_diff'] - mean) / sd
outliers = both[(abs(both['right_SD'])>1) | (abs(both['left_SD'])>1)].sort_values('left_SD', ascending=False).sort_values('right_SD', ascending=False)

outliers.to_csv("outliers.csv")
print(f'Saved {len(outliers)} outliers to outliers.csv')

