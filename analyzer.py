import csv
from time import strftime, localtime

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")
f_out = None

def match_prefix(s, prefix):
    return s[:len(prefix)] == prefix, s[len(prefix):]

with open("results.txt", "r") as f_in:
    for line in f_in.readlines():
        timestamp = float(line[24:41])
        message = line[42:].strip()
        is_match, suffix = match_prefix(message, "Filling in username: ")
        if is_match:
            filename = strftime("%Y%m%d_%H%M%S", localtime(timestamp)) + "_" + suffix + ".csv"
            if f_out is not None:
                f_out.close()
            f_out = open(filename, "w", newline = "")
            csv_out = csv.writer(f_out, dialect = "nl_excel")
            csv_out.writerow(["current_item", "next_item", "elapsed_time"])
            current_item = None
            current_timestamp = timestamp
        is_match, suffix = match_prefix(message, "Active item: ")
        if is_match:
            next_item = suffix
            next_timestamp = timestamp
            if current_item is not None:
                csv_out.writerow([current_item, next_item, next_timestamp - current_timestamp])
            current_item = next_item
            current_timestamp = next_timestamp
