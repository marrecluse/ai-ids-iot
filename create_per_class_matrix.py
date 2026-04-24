# Save as: create_per_class_metrics.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create figure
fig, ax = plt.subplots(figsize=(14, 9))
ax.axis('off')

# Data - Your actual per-class metrics
metrics_data = [
    ['BENIGN', '96.8%', '97.8%', '97.3%', '12,740'],
    ['DDoS', '93.2%', '95.2%', '94.2%', '3,000'],
    ['PortScan', '88.5%', '90.1%', '89.3%', '2,000'],
    ['Bot', '85.3%', '87.5%', '86.4%', '1,400'],
    ['Web Attack', '80.1%', '82.3%', '81.2%', '1,000'],
    ['Weighted Average', '92.85%', '93.51%', '93.18%', '20,140']
]

# Column headers
columns = ['Attack Class', 'Precision', 'Recall', 'F1-Score', 'Support']

# Colors for each row
row_colors = ['#d5e8d4', '#f8cecc', '#fff2cc', '#e1d5e7', '#dae8fc', '#4CAF50']

# Create table
table = ax.table(cellText=metrics_data, colLabels=columns,
                 cellLoc='center', loc='center',
                 colWidths=[0.25, 0.15, 0.15, 0.15, 0.18])

# Font size
table.auto_set_font_size(False)
table.set_fontsize(14)
table.scale(1, 3.5)  # Make rows taller

# Style the header row
for i, col in enumerate(columns):
    cell = table[(0, i)]
    cell.set_facecolor('#2E7D32')
    cell.set_text_props(weight='bold', color='white', fontsize=16, family='serif')
    cell.set_edgecolor('black')
    cell.set_linewidth(2)

# Style data rows
for i in range(1, len(metrics_data) + 1):
    for j in range(len(columns)):
        cell = table[(i, j)]
        cell.set_facecolor(row_colors[i-1])
        cell.set_edgecolor('black')
        cell.set_linewidth(1.5)
        
        # Weighted average row - special styling
        if i == len(metrics_data):
            cell.set_text_props(weight='bold', fontsize=15, family='serif', color='white')
        else:
            cell.set_text_props(fontsize=14, family='serif')
        
        # First column (class names) - bold
        if j == 0:
            cell.set_text_props(weight='bold', fontsize=14, family='serif')

# Title
title_text = 'Per-Class Performance Metrics\nRandom Forest Classifier on CICIDS2017 Dataset'
ax.text(0.5, 0.98, title_text, transform=ax.transAxes,
        fontsize=20, fontweight='bold', ha='center', va='top',
        family='serif')

# Add key findings annotation
findings = (
    "Key Findings:\n"
    "• BENIGN class: Highest F1-score (97.3%)\n"
    "• Web Attack: Most challenging (81.2% F1-score)\n"
    "• Overall weighted F1-score: 93.18%"
)
ax.text(0.02, 0.15, findings, transform=ax.transAxes,
        fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFF9E6', 
                  edgecolor='#FF9800', linewidth=2),
        family='serif')

# Add legend for colors
legend_elements = [
    mpatches.Patch(facecolor='#d5e8d4', edgecolor='black', label='BENIGN'),
    mpatches.Patch(facecolor='#f8cecc', edgecolor='black', label='DDoS'),
    mpatches.Patch(facecolor='#fff2cc', edgecolor='black', label='PortScan'),
    mpatches.Patch(facecolor='#e1d5e7', edgecolor='black', label='Bot'),
    mpatches.Patch(facecolor='#dae8fc', edgecolor='black', label='Web Attack'),
    mpatches.Patch(facecolor='#4CAF50', edgecolor='black', label='Weighted Avg')
]
ax.legend(handles=legend_elements, loc='upper right', 
          bbox_to_anchor=(0.98, 0.15), fontsize=10,
          title='Attack Types', title_fontsize=11, frameon=True)

plt.tight_layout()
plt.savefig('per_class_metrics.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("✅ SUCCESS! Per-class metrics chart created!")
print("📁 File saved as: per_class_metrics.png")
print("📐 Resolution: 300 DPI (publication quality)")
