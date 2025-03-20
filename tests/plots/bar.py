import matplotlib.pyplot as plt
import numpy as np
import textwrap

# Define the labels for the system configurations
systems = [
    "GPT-4o\nSingle agent",
    "GPT-4o\nMulti-agents",
    "Deepseek-r1\nSingle agent",
    "Deepseek-r1\nMulti-agents",
    "Llama-3.3-70B\nSingle agent",
    "Llama-3.3-70B\nMulti-agents",
    "GPT-4o\nMultimodal"
]

# ------------------------------
# Data provided from the results
# ------------------------------

# 1. Success rates (number of successful executions / total prompts * 100)
total_prompts = 57
success_counts = [52, 43, 21, 22, 46, 25, 52]
success_rate = [(count / total_prompts) * 100 for count in success_counts]

# 2. Average Processing Time (in seconds per prompt)
avg_time = [8.15, 23.50, 33.26, 46.57, 17.19, 22.15, 43.39]

# 3. Average Cost per Prompt (in USD)
avg_cost = [
    0.006345,  
    0.653967 / total_prompts,  
    0.0,  
    0.0,  
    0.064081 / total_prompts,  
    0.064081 / total_prompts,  
    3.29839 / total_prompts  
]

# 4. Average Tokens per Prompt
avg_tokens = [1583.5, 3045.61, 2815.3, 4735.65, 1836.0, 1765.61, 18346.49]

# ------------------------------
# Plotting
# ------------------------------

# Set a common style for plots
plt.style.use('seaborn-darkgrid' if 'seaborn-darkgrid' in plt.style.available else 'ggplot')

# Create a figure with four subplots
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
x = np.arange(len(systems))  # X-axis positions for bars
bar_width = 0.6  # Width of bars in bar chart

# Colors (black and white theme)
colors = ['black', 'dimgray', 'gray', 'darkgray', 'silver', 'lightgray', 'whitesmoke']

# Plot 1: Success Rate (%)
axs[0, 0].bar(x, success_rate, color=colors, width=bar_width)
axs[0, 0].set_title("Execution Success Rate (%)", fontsize=12)
axs[0, 0].set_xticks(x)
axs[0, 0].set_xticklabels(systems, rotation=0, ha='center')
axs[0, 0].set_ylabel("Success Rate (%)")
for i, rate in enumerate(success_rate):
    axs[0, 0].text(x[i], rate + 1, f"{rate:.1f}%", ha='center', fontsize=10)

# Plot 2: Average Processing Time (seconds)
axs[0, 1].bar(x, avg_time, color=colors, width=bar_width)
axs[0, 1].set_title("Average Processing Time (s)", fontsize=12)
axs[0, 1].set_xticks(x)
axs[0, 1].set_xticklabels(systems, rotation=0, ha='center')
axs[0, 1].set_ylabel("Time (s)")
for i, t in enumerate(avg_time):
    axs[0, 1].text(x[i], t + 0.5, f"{t:.2f}", ha='center', fontsize=10)

# Plot 3: Average Cost per Prompt (USD)
axs[1, 0].bar(x, avg_cost, color=colors, width=bar_width)
axs[1, 0].set_title("Average Cost per Prompt (USD)", fontsize=12)
axs[1, 0].set_xticks(x)
axs[1, 0].set_xticklabels(systems, rotation=0, ha='center')
axs[1, 0].set_ylabel("Cost (USD)")
for i, c in enumerate(avg_cost):
    axs[1, 0].text(x[i], c + 0.0005, f"${c:.5f}", ha='center', fontsize=10)

# Plot 4: Average Tokens per Prompt
axs[1, 1].bar(x, avg_tokens, color=colors, width=bar_width)
axs[1, 1].set_title("Average Tokens per Prompt", fontsize=12)
axs[1, 1].set_xticks(x)
axs[1, 1].set_xticklabels(systems, rotation=0, ha='center')
axs[1, 1].set_ylabel("Tokens")
for i, tok in enumerate(avg_tokens):
    axs[1, 1].text(x[i], tok + 30, f"{int(tok)}", ha='center', fontsize=10)

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("system_performance_analysis_bw.png", dpi=300)
plt.show()
