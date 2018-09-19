import csv
import sys
import os
from time import strftime, localtime

if len(sys.argv) < 2:
    print("Missing argument: input filename")
    exit(1)
in_filename = sys.argv[1]
out_filename_prefix = os.path.splitext(in_filename)[0]

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")
f_out = None

def match_prefix(s, prefix):
    return s[:len(prefix)] == prefix, s[len(prefix):]

with open(in_filename, "r") as f_in:
    for line in f_in.readlines():
        timestamp = float(line[24:41])
        message = line[42:].strip()
        is_match, suffix = match_prefix(message, "Filling in username: ")
        if is_match:
            filename = out_filename_prefix + "_" + suffix + ".csv"
            if f_out is not None:
                f_out.close()
            f_out = open(filename, "w", newline = "")
            csv_out = csv.writer(f_out, dialect = "nl_excel")
            csv_out.writerow(["time_since_login", "time_since_previous", "item"])
        is_match, _ = match_prefix(message, "Pressing login button")
        if is_match:
            prev_item = None
            prev_timestamp = None
            start_timestamp = timestamp
        is_match, suffix = match_prefix(message, "Active item: ")
        if is_match:
            next_item = suffix
            next_timestamp = timestamp
            csv_out.writerow([
                "{:.3f}".format(next_timestamp - start_timestamp), 
                "{:.3f}".format(next_timestamp - prev_timestamp) if prev_timestamp is not None else None, 
                next_item
            ])
            prev_timestamp = next_timestamp

        
