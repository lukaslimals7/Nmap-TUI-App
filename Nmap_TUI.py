import npyscreen
import subprocess
import threading
import time
from datetime import datetime


scanning = False
scan_thread = None
output_dir = "nmap_scans"

def run_nmap_scan(mode, target, output_widget):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/scan_{mode.strip('-')}_{timestamp}.txt"
    command = ["nmap", mode, "-oN", output_file, target]
    try:
        output_widget.add_line(f"Running {mode} on {target}...")
        subprocess.run(command, check=True)
        output_widget.add_line(f"Done: {output_file}")
    except subprocess.CalledProcessError as e:
        output_widget.add_line(f"Error: {e}")

def scan_loop(target, modes, interval, output_widget):
    global scanning
    subprocess.run(["mkdir", "-p", output_dir])
    while scanning:
        for mode in modes:
            if not scanning:
                break
            run_nmap_scan(mode, target, output_widget)
            time.sleep(interval)
        if scanning:
            output_widget.add_line("Cycle done.")

class NmapTUIApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Nmap TUI")

class MainForm(npyscreen.Form):
    def create(self):
        banner = """
        ~~~ Nmap TUI ~~~
           by ry0m3n
        """
        # Add banner at the top
        self.add(npyscreen.FixedText, value=banner, editable=False)
        
        self.target = self.add(npyscreen.TitleText, name="Target:", value="127.0.0.1")
        self.interval = self.add(npyscreen.TitleText, name="Interval (s):", value="300")
        self.modes = self.add(npyscreen.TitleMultiSelect, name="Modes:",
                              values=["-sS", "-sU", "-sT", "-sN", "-A", "-p-", "-T4", "-T1"], max_height=4, scroll_exit=True)
        self.output = self.add(npyscreen.MultiLineEdit, name="Output", value="Output...\n",
                              max_height=5, editable=False)  # Reduced height
        self.add(npyscreen.ButtonPress, name="Start", when_pressed_function=self.start_scan)
        self.add(npyscreen.ButtonPress, name="Stop", when_pressed_function=self.stop_scan)
        self.add(npyscreen.ButtonPress, name="Exit", when_pressed_function=self.exit_app)

    def start_scan(self):
        global scanning, scan_thread
        if scanning:
            self.output.value += "Already running!\n"
            self.output.display()
            return
        target = self.target.value
        interval = int(self.interval.value)
        selected_modes = [self.modes.values[i] for i in self.modes.value]
        if not selected_modes:
            self.output.value += "Select a mode!\n"
            self.output.display()
            return
        scanning = True
        self.output.value += "Starting...\n"
        self.output.display()
        scan_thread = threading.Thread(target=scan_loop, args=(target, selected_modes, interval, self))
        scan_thread.start()

    def stop_scan(self):
        global scanning
        scanning = False
        self.output.value += "Stopping...\n"
        self.output.display()

    def exit_app(self):
        global scanning
        scanning = False
        self.parentApp.setNextForm(None)
        self.editing = False

    def add_line(self, text):
        self.output.value += f"{text}\n"
        self.output.display()

if __name__ == "__main__":
    app = NmapTUIApp()
    app.run()
