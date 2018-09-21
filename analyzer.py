import csv
import sys
import os
from time import strftime, localtime

def match_prefix(s, prefix):
    return s[:len(prefix)] == prefix, s[len(prefix):]

action_lines = [
    "Starting browser: ",
    "Traversal method: ",
    "Filling in username: ",
    "Pressing login button",
    "Navigating to next menu item",
    "Navigating to menu item",
    "Active item: ",
    "Not on first page",
    "Closing browser",
    "Login complete",
    "Navigation complete"
]

if len(sys.argv) < 2:
    print("Missing argument: input filename")
    exit(1)
in_filename = sys.argv[1]
out_filename_prefix = os.path.splitext(in_filename)[0]

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")
f_out = open(out_filename_prefix + "_clean.csv", "w", newline = "", encoding = "utf-8")
csv_out = csv.writer(f_out, dialect = "nl_excel")
csv_out.writerow(["browser", "methode", "run_nr", "gebruikersnaam", "laadtijd", "item"])

runs = {}
buffer = []

silent = False
browser = None
traversal_method = None
username = None
start_time = None
end_time = None
item = None
with open(in_filename, "r", encoding = "utf-8") as f_in:
    for line in f_in.readlines():
        timestamp = float(line[24:41])
        message = line[42:].strip()
        for action_line in action_lines:
            is_match, suffix = match_prefix(message, action_line)
            if is_match:
                if action_line == action_lines[0]:
                    browser = suffix
                elif action_line == action_lines[1]:
                    traversal_method = suffix
                elif action_line == action_lines[2]:
                    username = suffix
                    if username not in runs:
                        runs[username] = 1
                elif action_line == action_lines[3] or action_line == action_lines[4] or action_line == action_lines[5]:
                    start_time = timestamp
                elif action_line == action_lines[6]:
                    item = suffix
                    buffer.append([browser, traversal_method, runs[username], username, "{:.3f}".format(end_time - start_time).replace(".", ","), item])
                elif action_line == action_lines[7]:
                    silent = True
                elif action_line == action_lines[8]:
                    if not silent:
                        for output in buffer:
                            csv_out.writerow(output)
                        runs[username] += 1
                    buffer = []
                    silent = False
                elif action_line == action_lines[9] or action_line == action_lines[10]:
                    end_time = timestamp
                break
