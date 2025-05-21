import matplotlib.pyplot as plt
from datetime import datetime

# File location
FILE_PATH = "cot.txt"

# Read the local file
with open(FILE_PATH, "r") as file:
    lines = file.readlines()

# Extract only BTC lines (Product Code: "XBT" under CME group)
btc_lines = [line for line in lines if "XBT" in line]

if len(btc_lines) < 2:
    raise ValueError("Not enough BTC data found in cot.txt. Make sure it's the correct file.")

# Get latest two weeks (last one is most recent)
last_week = btc_lines[-2].split(",")
this_week = btc_lines[-1].split(",")

# Define the relevant categories (e.g. Asset Manager, Leveraged Funds)
labels = ["Asset Long", "Asset Short", "Lev Long", "Lev Short"]

# Column indices may differ depending on format.
# These work for the CME TFF short format CSV (check column layout if unsure):
this_data = [
    int(this_week[8]),   # Asset Manager Long
    int(this_week[9]),   # Asset Manager Short
    int(this_week[14]),  # Leveraged Funds Long
    int(this_week[15]),  # Leveraged Funds Short
]

last_data = [
    int(last_week[8]),
    int(last_week[9]),
    int(last_week[14]),
    int(last_week[15]),
]

# Plotting
x = range(len(labels))
bar_width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x, last_data, width=bar_width, label="Last Week", color="lightgray")
plt.bar([i + bar_width for i in x], this_data, width=bar_width, label="This Week", color="skyblue")

plt.xticks([i + bar_width / 2 for i in x], labels)
plt.ylabel("Contracts")
plt.title("Bitcoin CME Futures COT: This Week vs Last Week")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Save chart
timestamp = datetime.now().strftime("%Y-%m-%d")
plt.tight_layout()
plt.savefig(f"btc_cot_comparison_{timestamp}.png", dpi=300)
plt.show()