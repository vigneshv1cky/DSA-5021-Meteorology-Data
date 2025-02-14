##############################################
# Libraries and Helper Functions
##############################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
import os
from urllib.request import urlopen


def grabfile(urlfront, filename, filedir=""):  # filedir could be data/, for example
    urlpath = urlfront + filename
    filepath = filedir + filename
    if os.path.exists(filepath):
        print(filepath, " already exists.  Delete it, if you want to overwrite.")
        return
    with urlopen(urlpath) as response:
        body = response.read()
    with open(filepath, "wb") as f:
        f.write(body)
    print("downloaded " + urlpath + " to " + filepath)
    return


##############################################
# User Information and File Selection
##############################################

yourname = "Vignesh Murugan"  # This label is put on your figures
siteinfo = {
    "31011": "CAIRNS AERO",
    "12038": "KALGOORLIE-BOULDER AIRPORT",
    "09021": "PERTH AIRPORT",
}
filenames = [
    "31011_AIR_TEMP_MAX.csv",
    "12038_AIR_TEMP_MAX.csv",
    "09021_AIR_TEMP_MAX.csv",
    "31011_AIR_TEMP_MIN.csv",
    "12038_AIR_TEMP_MIN.csv",
    "09021_AIR_TEMP_MIN.csv",
]

usefile = 0  # Choose a file index
infilename = filenames[usefile]
print(f"You chose: {infilename}")

# Download the file if it doesn't exist
if not os.path.exists(infilename):
    grabfile("http://dsa5021.net/data/", infilename)
else:
    print(f"You already have {infilename}")

# Extract site information
sitenum = infilename.split("_")[0]
sitename = siteinfo[sitenum]
varname = infilename[len(sitenum) + 1 : -4]
print(f"This is what you are studying:\n{sitenum}\n{sitename}\n{varname}")

##############################################
# Data Loading and Cleaning
##############################################

# Load the data into a Pandas DataFrame
df = pd.read_csv(infilename, delim_whitespace=True)

# Rename columns for better clarity
df.columns = ["epoch", "ob", "clim", "f1", "f2", "f3", "f4", "f5", "f6", "f7"]

# Convert epoch to human-readable date
df["date"] = pd.to_datetime(df["epoch"], unit="s")
df.set_index("date", inplace=True)

# Replace "NA" with NaN and drop rows with missing values
df.replace("NA", np.nan, inplace=True)
df = df.dropna().astype(float)
df

##############################################
# Error Metrics Calculation
##############################################


# Root Mean Square Error and Mean Absolute Error calculations
def calculate_errors(obs, pred):
    rmse = np.sqrt(np.mean((obs - pred) ** 2))
    mae = np.mean(np.abs(obs - pred))
    return rmse, mae


# Calculate RMSE and MAE for climatology
rmse_clim, mae_clim = calculate_errors(df["ob"], df["clim"])
print(f"RMSE (Clim): {rmse_clim:.3f}, MAE (Clim): {mae_clim:.3f}")

# Evaluate RMSE and MAE for forecasts (f1 to f7)
skills = []
for col in ["f1", "f2", "f3", "f4", "f5", "f6", "f7"]:
    rmse, mae = calculate_errors(df["ob"], df[col])
    skill_score = 1 - (rmse / rmse_clim)  # RMSE skill score
    skills.append(skill_score)
    print(f"{col}: RMSE = {rmse:.3f}, Skill = {skill_score:.3f}")

##############################################
# Visualizations
##############################################

# Plot observation, climatology, and a forecast
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["ob"], "g-", label="Observation")
plt.plot(df.index, df["clim"], "r--", label="Climatology")
plt.plot(df.index, df["f1"], "b-", label="Forecast (f1)")
plt.legend()
plt.title(f"Observation vs Climatology and Forecast ({sitename})")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.savefig("observation_vs_clim_forecast.png")
plt.show()

##############################################
# Bar Plot of RMSE Skill Scores
##############################################

plt.figure(figsize=(10, 5))
plt.bar(["f1", "f2", "f3", "f4", "f5", "f6", "f7"], skills, color="blue")
plt.title(f"RMSE Skill Scores for Forecasts ({sitename})")
plt.ylabel("Skill Score")
plt.xlabel("Forecasts")
plt.savefig("rmse_skill_scores.png")
plt.show()

##############################################
# Scatter Plots: Observation vs Forecasts/Climatology
##############################################

fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor="yellow")
forecast_cols = ["f1", "f7"]
colors = ["blue", "green"]

for ax, col, color in zip(axes[:2], forecast_cols, colors):
    ax.scatter(df[col], df["ob"], color=color, alpha=0.6)
    ax.plot([df["ob"].min(), df["ob"].max()], [df["ob"].min(), df["ob"].max()], "k--")
    ax.set_title(f"Observation vs {col.upper()} (Skill: {skills[int(col[1]) - 1]:.2f})")
    ax.set_xlabel(f"{col.upper()} Forecast")
    ax.set_ylabel("Observation")
    ax.grid()

# Plot for climatology
axes[2].scatter(df["clim"], df["ob"], color="red", alpha=0.6)
axes[2].plot([df["ob"].min(), df["ob"].max()], [df["ob"].min(), df["ob"].max()], "k--")
axes[2].set_title("Observation vs Climatology (Skill: 0.00)")
axes[2].set_xlabel("Climatology")
axes[2].set_ylabel("Observation")
axes[2].grid()

plt.tight_layout()
plt.savefig(f"{varname}_scatter_plots.png")
plt.show()

##############################################
# Line Plot: Observation vs Individual Forecasts
##############################################


def plot_forecast(df, col, title):
    plt.figure(figsize=(15, 5))
    plt.plot(df.index, df["ob"], "r-", label="Observation")
    plt.plot(df.index, df[col], "b-", label=col.upper())
    # plt.fill_between(
    #     df.index,
    #     df["ob"],
    #     df[col],
    #     where=(df["ob"] > df[col]),
    #     interpolate=True,
    #     color="red",
    #     alpha=0.3,
    #     label="Under-prediction",
    # )
    # plt.fill_between(
    #     df.index,
    #     df["ob"],
    #     df[col],
    #     where=(df["ob"] < df[col]),
    #     interpolate=True,
    #     color="blue",
    #     alpha=0.3,
    #     label="Over-prediction",
    # )
    plt.legend()
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid()
    plt.savefig(f"{col}_forecast_plot.png")
    plt.show()


for col in ["f1", "f2", "f3", "f4", "f5", "f6", "f7"]:
    plot_forecast(df, col, f"Observation vs {col.upper()} ({sitename})")
