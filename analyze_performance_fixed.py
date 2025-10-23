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
    current_case = None
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for test case headers
        if "Copy with TMA load and store -- no swizzling" in line:
            current_case = {
                'name': 'TMA No Swizzling',
                'multicast': False,
                'deep_copy': '1X',
                'times': []
            }
        elif "Copy with TMA Multicast load and store" in line:
            current_case = {
                'name': 'TMA Multicast',
                'multicast': True,
                'deep_copy': None,  # Will be set by next line
                'times': []
            }
        elif "Copy with TMA load and store, NO multicast" in line:
            current_case = {
                'name': 'TMA No Multicast',
                'multicast': False,
                'deep_copy': None,  # Will be set by next line
                'times': []
            }
        elif current_case and line.startswith("Trial") and "Completed in" in line:
            # Extract time from trial line
            match = re.search(r'Completed in ([\d.]+)ms', line)
            if match:
                time_ms = float(match.group(1))
                current_case['times'].append(time_ms)
        elif line.startswith("Success") and current_case and current_case['times']:
            # End of current test case
            test_cases.append(current_case.copy())
            current_case = None
        
        # Check for deep copy information in the next few lines
        if current_case and current_case['deep_copy'] is None:
            # Look ahead for deep copy information
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                if "Deep copy 2X" in next_line:
                    current_case['deep_copy'] = '2X'
                    break
                elif "Deep copy 4X" in next_line:
                    current_case['deep_copy'] = '4X'
                    break
        
        i += 1
    
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
    # Group test cases by name and deep copy factor
    grouped_cases = defaultdict(list)
    
    for case in test_cases:
        key = f"{case['name']} ({case['deep_copy']})"
        grouped_cases[key].append(case)
    
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
    
    for key, cases in grouped_cases.items():
        # Combine all times for this test case
        all_times = []
        for case in cases:
            all_times.extend(case['times'])
        
        if all_times:
            stats = calculate_statistics(all_times)
            case_names.append(key)
            means.append(stats['mean'])
            stds.append(stats['std'])
            
            # Determine color based on test type
            if 'No Swizzling' in key:
                colors.append(color_map['TMA No Swizzling'])
            elif 'Multicast' in key and 'NO multicast' not in key:
                colors.append(color_map['TMA Multicast'])
            else:
                colors.append(color_map['TMA No Multicast'])
    
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
    output_file = '/mnt/myspace/cdb/cfx-article-src/performance_analysis.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    
    # Also save as PDF for better quality
    pdf_file = '/mnt/myspace/cdb/cfx-article-src/performance_analysis.pdf'
    fig.savefig(pdf_file, bbox_inches='tight')
    print(f"PDF saved to: {pdf_file}")
    
    plt.show()

if __name__ == "__main__":
    main()

