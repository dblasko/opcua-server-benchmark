from datetime import datetime
import re

if __name__ == "__main__":
    with open('logfile.log', 'r') as f:
        lines = f.readlines()

    timestamps = []
    for line in lines:
        match = re.search(r'Timestamp=(datetime\.datetime\(([\d, ]+)\))', line)
        if match:
            timestamp_str = match.group(2)
            timestamp = datetime.strptime(timestamp_str, '%Y, %m, %d, %H, %M, %S, %f')
            timestamps.append(timestamp)

    print("Timestamps:")
    for i, timestamp in enumerate(timestamps):
        print(f"Timestamp {i+1}: {timestamp}")