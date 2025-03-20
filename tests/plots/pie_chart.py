import matplotlib.pyplot as plt
import numpy as np

# Data from the table with corrected count for hard prompts
categories = ['Easy Prompts', 'Medium Prompts', 'Hard Prompts']
total_counts = [33, 33, 34]  # Corrected count for hard prompts

# First section data - Execution Success vs Failures
execution_success = [33, 33, 31]
execution_failures = [0, 0, 2]  # Adjusted to account for 34 total hard prompts

# Second section data - Breakdown of Execution Success
cad_fully_success = [32, 22, 12]
spatial_reasoning_failure = [0, 6, 14]
wrong_model_creation = [1, 5, 5]

# Create figure with 2 rows of 3 pie charts
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Set transparent background for figure and axes
fig.patch.set_facecolor('none')
for ax in axes.flatten():
    ax.patch.set_facecolor('none')

# Colors for pie charts
success_failure_colors = ['#4CAF50', '#F44336']  # Green for success, red for failure
success_breakdown_colors = ['#4CAF50', '#FFC107', '#FF9800']  # Different colors for success types

# First row: Execution Success vs Failures
for i, category in enumerate(categories):
    data = [execution_success[i], execution_failures[i]]
    
    wedges, _, autotexts = axes[0, i].pie(
        data, 
        labels=None, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=success_failure_colors
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
        autotext.set_color('white')
    
    axes[0, i].set_title(f'{category} (n={total_counts[i]})\nExecution Success vs Failures')
    axes[0, i].axis('equal')

# Create legend for first row on the middle chart
legend_elements_row1 = [
    plt.Rectangle((0,0), 1, 1, color=success_failure_colors[0], label='Execution Success'),
    plt.Rectangle((0,0), 1, 1, color=success_failure_colors[1], label='Execution Failures')
]
axes[0, 1].legend(handles=legend_elements_row1, loc='lower center', bbox_to_anchor=(0.5, -0.15))

# Second row: Breakdown of Execution Success
for i, category in enumerate(categories):
    data = [cad_fully_success[i], spatial_reasoning_failure[i], wrong_model_creation[i]]
    
    non_zero_data = []
    non_zero_colors = []
    for j, value in enumerate(data):
        if value > 0:
            non_zero_data.append(value)
            non_zero_colors.append(success_breakdown_colors[j])
    
    wedges, _, autotexts = axes[1, i].pie(
        non_zero_data, 
        labels=None, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=non_zero_colors
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
        autotext.set_color('white')
    
    axes[1, i].set_title(f'Successfully Executed {category} (n={execution_success[i]})\nBreakdown of Execution Success')
    axes[1, i].axis('equal')

# Create legend for second row on the middle chart
legend_elements_row2 = [
    plt.Rectangle((0,0), 1, 1, color=success_breakdown_colors[0], label='CAD creation fully success'),
    plt.Rectangle((0,0), 1, 1, color=success_breakdown_colors[1], label='CAD created but failure due to spatial reasoning'),
    plt.Rectangle((0,0), 1, 1, color=success_breakdown_colors[2], label='CAD created but failure due to other reasons')
]
axes[1, 1].legend(handles=legend_elements_row2, loc='lower center', bbox_to_anchor=(0.5, -0.15))

plt.tight_layout(h_pad=2)
plt.subplots_adjust(bottom=0.15)

plt.savefig('cad_prompt_success_analysis_reveiw_3.png', dpi=300, bbox_inches='tight')
plt.show()
