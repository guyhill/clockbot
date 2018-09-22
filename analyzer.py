import csv
import sys
import os

csv.register_dialect("nl_excel", csv.excel, delimiter = ";")

class ClockbotLogMiner:

    def __init__(self, filename):
        self.f_in = open(filename, "r", encoding = "utf-8")
        
        out_filename = os.path.splitext(in_filename)[0] + "_timedata.csv"
        self.f_out = open(out_filename, "w", newline = "", encoding = "utf-8")
        self.csv_out = csv.writer(self.f_out, dialect = "nl_excel")
        self.csv_out.writerow(["browser", "methode", "run_nr", "gebruikersnaam", "laadtijd", "item"])

        self.runs = {}
        self.buffer = []

        self.silent = False
        self.browser = None
        self.traversal_method = None
        self.username = None
        self.start_time = None
        self.end_time = None
        self.item = None

    def process_all(self):
        for line in self.f_in.readlines():
            timestamp = float(line[24:41])
            message = line[42:].strip()
            
            for action_line, handler in self.action_lines:
                is_match = message[:len(action_line)] == action_line
                suffix = message[len(action_line):]
                if is_match:
                    handler(self, timestamp, suffix)
                    break

    def set_browser_name(self, t, browser_name):
        self.browser = browser_name

    def set_traversal_method(self, t, traversal_method):
        self.traversal_method = traversal_method

    def set_username(self, t, username):
        self.username = username
        if self.username not in self.runs:
            self.runs[self.username] = 1

    def set_start_time(self, timestamp, s):
        self.start_time = timestamp

    def set_end_time(self, timestamp, s):
        self.end_time = timestamp

    def set_item(self, t, item):
        self.item = item
        self.buffer.append([
            self.browser, 
            self.traversal_method, 
            self.runs[self.username], 
            self.username, 
            "{:.3f}".format(self.end_time - self.start_time).replace(".", ","), 
            self.item
        ])

    def set_silent(self, t, s):
        self.silent = True

    def write_data(self, t, s):
        if not self.silent:
            for output in self.buffer:
                self.csv_out.writerow(output)
            self.runs[self.username] += 1
        self.buffer = []
        self.silent = False

    action_lines = [
        ("Starting browser: ", set_browser_name),
        ("Traversal method: ", set_traversal_method),
        ("Filling in username: ", set_username),
        ("Pressing login button", set_start_time),
        ("Navigating to first menu item", set_start_time),
        ("Navigating to next menu item", set_start_time),
        ("Navigating to menu item", set_start_time),
        ("Active item: ", set_item),
        ("Not on first page", set_silent),
        ("Closing browser", write_data),
        ("Login complete", set_end_time),
        ("Navigation complete", set_end_time)
    ]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing argument: input filename")
        exit(1)
    in_filename = sys.argv[1]

    clm = ClockbotLogMiner(in_filename)
    clm.process_all()
