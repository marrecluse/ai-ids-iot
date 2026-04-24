# Save this as: create_model_performance_chart.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Data
models = ['Baseline\n(Majority Class)', 'Logistic\nRegression', 'SVM', 'Random Forest\n(Proposed)', 'Gradient\nBoosting']
accuracies = [84.79, 87.32, 90.31, 94.23, 93.15]
colors = ['#f8cecc', '#fff2cc', '#dae8fc', '#d5e8d4', '#e1d5e7']

# Create figure
fig, ax = plt.subplots(figsize=(14, 8))

# Create bars
bars = ax.bar(models, accuracies, color=colors, edgecolor='black', linewidth=2, width=0.65)

# Highlight Random Forest (the proposed model)
bars[3].set_edgecolor('#2E7D32')
bars[3].set_linewidth(4)

# Formatting
ax.set_ylabel('Accuracy (%)', fontsize=18, fontweight='bold', fontfamily='serif')
ax.set_xlabel('Classification Models', fontsize=18, fontweight='bold', fontfamily='serif')
ax.set_title('Model Performance Comparison on CICIDS2017 Dataset', 
             fontsize=22, fontweight='bold', fontfamily='serif', pad=25)

# Set y-axis
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])

# Grid
ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.2, color='gray')
ax.set_axisbelow(True)

# Add value labels on top of bars
for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 2,
            f'{acc}%', ha='center', va='bottom', 
            fontweight='bold', fontsize=16, fontfamily='serif')

# Add star to Random Forest
ax.text(3, 97.5, '⭐', ha='center', fontsize=45)

# Add "Best Performance" label
ax.text(3, 88, 'Best\nPerformance', ha='center', va='center',
        fontsize=12, fontweight='bold', style='italic', 
        color='#2E7D32', fontfamily='serif',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', 
                  edgecolor='#2E7D32', linewidth=2))

# Add improvement annotation
ax.annotate('', xy=(3, 94.23), xytext=(0, 84.79),
            arrowprops=dict(arrowstyle='->', lw=2.5, color='#1976D2'))
ax.text(1.5, 89.5, '+9.44%\nimprovement', ha='center',
        fontsize=11, fontweight='bold', color='#1976D2',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                  edgecolor='#1976D2', linewidth=1.5))

# Add summary box
summary_text = (
    "Random Forest achieves highest accuracy (94.23%)\n"
    "Outperforms baseline by 9.44 percentage points\n"
    "Dataset: CICIDS2017 | Test Split: 60/20/20"
)
ax.text(0.5, 0.98, summary_text, transform=ax.transAxes,
        fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#F5F5F5', 
                  edgecolor='#666666', linewidth=2),
        fontfamily='serif')

# Tick styling
ax.tick_params(axis='both', labelsize=13)
plt.xticks(fontweight='semibold')

# Tight layout
plt.tight_layout()

# Save with high quality
plt.savefig('model_performance_chart.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("✅ SUCCESS! Chart saved as: model_performance_chart.png")
print("📁 Location: Current directory")
print("📐 Resolution: 300 DPI (publication quality)")

# Also display (optional)
plt.show()
