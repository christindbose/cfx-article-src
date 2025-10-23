#!/usr/bin/env python3
"""
Parse TMA performance data and create plots with average times and error bars.
"""

import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_performance_data(filename):
    """Parse the performance data from the output file."""
    test_cases = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split into sections based on "Copy with" headers
    sections = re.split(r'(Copy with.*)', content)
    
    current_section = None
    current_deep_copy = None
    
    for i, section in enumerate(sections):
        if section.startswith("Copy with"):
            # This is a new test case header
            current_section = section.strip()
            current_deep_copy = None
        elif "Deep copy 2X" in section:
            current_deep_copy = "2X"
        elif "Deep copy 4X" in section:
            current_deep_copy = "4X"
        elif current_section and "Trial" in section:
            # Extract trial data
            times = []
            for line in section.split('\n'):
                if "Trial" in line and "Completed in" in line:
                    match = re.search(r'Completed in ([\d.]+)ms', line)
                    if match:
                        times.append(float(match.group(1)))
            
            if times:
                # Determine test case name and type
                if "no swizzling" in current_section:
                    name = "TMA No Swizzling"
                    multicast = False
                    deep_copy = "1X"  # This is the baseline case
                elif "Multicast" in current_section and "NO multicast" not in current_section:
                    name = "TMA Multicast"
                    multicast = True
                    deep_copy = current_deep_copy or "Unknown"
                elif "NO multicast" in current_section:
                    name = "TMA No Multicast"
                    multicast = False
                    deep_copy = current_deep_copy or "Unknown"
                else:
                    continue
                
                test_cases.append({
                    'name': name,
                    'multicast': multicast,
                    'deep_copy': deep_copy,
                    'times': times
                })
    
    return test_cases

def calculate_statistics(times):
    """Calculate mean, std, and other statistics for a list of times."""
    times_array = np.array(times)
    return {
        'mean': np.mean(times_array),
        'std': np.std(times_array),
        'min': np.min(times_array),
        'max': np.max(times_array),
        'count': len(times_array)
    }

def create_plot(test_cases):
    """Create a plot showing average times with error bars."""
    # Sort test cases by name and deep copy for consistent ordering
    test_cases.sort(key=lambda x: (x['name'], x['deep_copy']))
    
    # Prepare data for plotting
    case_names = []
    means = []
    stds = []
    colors = []
    
    # Color mapping for different test types
    color_map = {
        'TMA No Swizzling': 'blue',
        'TMA Multicast': 'red', 
        'TMA No Multicast': 'green'
    }
    
    for case in test_cases:
        if case['times']:
            stats = calculate_statistics(case['times'])
            case_names.append(f"{case['name']} ({case['deep_copy']})")
            means.append(stats['mean'])
            stds.append(stats['std'])
            
            # Determine color based on test type
            colors.append(color_map[case['name']])
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x_pos = np.arange(len(case_names))
    bars = ax.bar(x_pos, means, yerr=stds, capsize=5, color=colors, alpha=0.7, 
                  edgecolor='black', linewidth=1)
    
    # Customize the plot
    ax.set_xlabel('Test Case', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    ax.set_title('TMA Performance Comparison\nAverage Time with Error Bars', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(case_names, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(i, mean + std + 0.01, f'{mean:.3f}±{std:.3f}', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    # Create legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor=color_map['TMA No Swizzling'], alpha=0.7, label='TMA No Swizzling'),
        plt.Rectangle((0,0),1,1, facecolor=color_map['TMA Multicast'], alpha=0.7, label='TMA Multicast'),
        plt.Rectangle((0,0),1,1, facecolor=color_map['TMA No Multicast'], alpha=0.7, label='TMA No Multicast')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    return fig

def print_summary(test_cases):
    """Print a summary of the performance data."""
    print("Performance Analysis Summary")
    print("=" * 50)
    
    # Sort for consistent output
    test_cases.sort(key=lambda x: (x['name'], x['deep_copy']))
    
    for case in test_cases:
        if case['times']:
            stats = calculate_statistics(case['times'])
            print(f"\n{case['name']} ({case['deep_copy']})")
            print(f"  Mean: {stats['mean']:.3f} ms")
            print(f"  Std:  {stats['std']:.3f} ms")
            print(f"  Min:  {stats['min']:.3f} ms")
            print(f"  Max:  {stats['max']:.3f} ms")
            print(f"  Trials: {stats['count']}")

def main():
    """Main function to parse data and create plots."""
    filename = '/mnt/myspace/cdb/cfx-article-src/tma/out.txt'
    
    # Parse the data
    test_cases = parse_performance_data(filename)
    
    # Print summary
    print_summary(test_cases)
    
    # Create and save the plot
    fig = create_plot(test_cases)
    output_file = '/mnt/myspace/cdb/cfx-article-src/performance_analysis_correct.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    
    # Also save as PDF for better quality
    pdf_file = '/mnt/myspace/cdb/cfx-article-src/performance_analysis_correct.pdf'
    fig.savefig(pdf_file, bbox_inches='tight')
    print(f"PDF saved to: {pdf_file}")
    
    plt.show()

if __name__ == "__main__":
    main()

