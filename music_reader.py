"""
CSV Playlist Reader

Read a CSV playlist (format: music,artist,album) and display it as a bar chart.

type '$ py Music_Reader.py [file list]' to use

"""

import csv
import os
import argparse
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib as mpl


def setup_font():
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    mpl.rcParams['axes.unicode_minus'] = False


def process_file(filepath, sort_order, width, height):
    counter = Counter()
    try:
        with open(filepath, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    counter[row[1]] += 1
    except Exception as e:
        print(f"Error: Failed to read [{filepath}]: {str(e)}")
        return

    if sort_order == 'desc':
        data = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    elif sort_order == 'asc':
        data = sorted(counter.items(), key=lambda x: x[1])
    else:  # 'none'
        data = list(counter.items())

    if not data:
        print(f"Error: No valid data in [{filepath}]")
        return

    categories, counts = zip(*data)
    total = sum(counts)

    filename = os.path.basename(filepath)
    fig = plt.figure(figsize=(width, height))
    fig.canvas.manager.set_window_title(filename)

    bars = plt.bar(categories, counts, color='skyblue', edgecolor='black')

    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout(pad=3.0)

    plt.title(f'{filename}', fontsize=14)
    plt.xlabel('Artist', fontsize=12)
    plt.ylabel('Count', fontsize=12)

    plt.text(0.98, 0.98, f'total: {Total}',
             transform=fig.transFigure,
             fontsize=13, fontweight='bold', color='darkred',
             ha='right', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray', alpha=0.8))

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f'{h}',
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')


def main():
    setup_font()

    parser = argparse.ArgumentParser(description='Generate category distribution bar chart from CSV.')
    parser.add_argument('files', type=str, nargs='+', help='Path(s) to the CSV file(s)')
    parser.add_argument('--sort', choices=['asc', 'desc', 'none'], default='desc',
                        help='Sort order: asc (ascending), desc (descending), none (original order)')
    parser.add_argument('--width', type=float, default=14, help='Figure width in inches (default: 14)')
    parser.add_argument('--height', type=float, default=7, help='Figure height in inches (default: 7)')
    args = parser.parse_args()

    for filepath in args.files:
        process_file(filepath, args.sort, args.width, args.height)

    plt.show()


if __name__ == '__main__':
    main()
