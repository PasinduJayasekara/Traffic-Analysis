import csv
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from collections import defaultdict


def process_csv_data(file_name):
    with open(file_name, "r") as file:
        return list(csv.DictReader(file))


def display_outcomes(outcomes, file_name):
    total_vehicles = len(outcomes)
    total_trucks = [r for r in outcomes if r["VehicleType"].lower() == "truck"]
    total_electric_vehicles = [r for r in outcomes if r["elctricHybrid"].lower() == "true"]
    total_two_wheeled = [r for r in outcomes if r["VehicleType"].lower() in {"bicycle", "motorcycle", "scooter"}]
    total_buses_north = [r for r in outcomes if r["JunctionName"] == "Elm Avenue/Rabbit Road"
                         and r["travel_Direction_out"] == "N"
                         and r["VehicleType"].lower() == "buss"]
    no_turn = [r for r in outcomes if r["travel_Direction_in"] == r["travel_Direction_out"]]
    over_speed = [r for r in outcomes if int(r["VehicleSpeed"]) > int(r["JunctionSpeedLimit"])]
    elm = [r for r in outcomes if r["JunctionName"] == "Elm Avenue/Rabbit Road"]
    hanley = [r for r in outcomes if r["JunctionName"] == "Hanley Highway/Westway"]
    total_scooters = [r for r in outcomes if r["VehicleType"].lower() == "scooter"
                      and r["JunctionName"] == "Elm Avenue/Rabbit Road"]

    peak_hours = defaultdict(int)
    for r in hanley:
        hour = r["timeOfDay"].split(":")[0]
        peak_hours[hour] += 1
    busiest_count = max(peak_hours.values(), default=0)
    peak_times = [f"Between {int(h):02d}:00 and {int(h)+1:02d}:00"
                  for h, c in peak_hours.items() if c == busiest_count]

    rainy_hours = [r["timeOfDay"].split(":")[0] for r in outcomes
                   if "Weather_Conditions" in r
                   and r["Weather_Conditions"].strip().lower() in ["light rain", "heavy rain"]]

    outputs = {
        "File Name": file_name,
        "Total Vehicles": total_vehicles,
        "Total Trucks": len(total_trucks),
        "Total Electric Vehicles": len(total_electric_vehicles),
        "Total Two-Wheeled Vehicles": len(total_two_wheeled),
        "Total Buses Heading North": len(total_buses_north),
        "Vehicles Without Turn": len(no_turn),
        "Trucks %": round(len(total_trucks) / total_vehicles * 100) if total_vehicles else 0,
        "Avg Bicycles/Hour": round(len([r for r in outcomes if r["VehicleType"].lower() == "bicycle"]) / 24),
        "Over Speed Vehicles": len(over_speed),
        "Elm Junction": len(elm),
        "Hanley Junction": len(hanley),
        "Scooter % Elm": round(len(total_scooters) / len(elm) * 100) if elm else 0,
        "Peak Vehicles in Hour": busiest_count,
        "Peak Times": peak_times,
        "Rainy Hours": len(set(rainy_hours))
    }
    return outputs


class HistogramApp:
    def __init__(self, traffic_data, date):
        self.traffic_data = traffic_data
        self.date = date
        self.root = tk.Toplevel()
        self.canvas = tk.Canvas(self.root, width=900, height=650, bg="white")

    def setup_window(self):
        self.root.title("Histogram")
        self.canvas.pack()

    def draw_histogram(self):
        max_vehicles = max((max(self.traffic_data[j].values()) for j in self.traffic_data), default=1)
        bar_width = 15
        x_offset, y_offset, y_scale = 30, 550, 400 / max_vehicles
        colors = {"Elm Avenue/Rabbit Road": "green", "Hanley Highway/Westway": "red"}

        for hour in range(24):
            x_base = x_offset + hour * 35
            for idx, (junction, hours) in enumerate(self.traffic_data.items()):
                count = hours.get(f"{hour:02d}", 0)
                bar_height = count * y_scale
                x = x_base + idx * bar_width
                y = y_offset - bar_height
                self.canvas.create_rectangle(x, y, x + bar_width, y_offset, fill=colors[junction])
                if count > 0:
                    self.canvas.create_text(x + bar_width // 2, y - 10, text=str(count), font=("Arial", 8))
            self.canvas.create_text(x_base + bar_width, y_offset + 15, text=f"{hour:02d}", font=("Arial", 10))

        self.canvas.create_text(450, 600, text="Hours 00:00 to 23:00", font=("Arial", 10))
        self.canvas.create_text(325, 30,
            text=f"Histogram of Vehicle Frequency per Hour ({self.date[0]:02d}/{self.date[1]:02d}/{self.date[2]})",
            font=("Arial", 16, "bold"))
        self.add_legend()

    def add_legend(self):
        self.canvas.create_rectangle(100, 50, 150, 70, fill="green")
        self.canvas.create_text(160, 60, text="Elm Avenue / Rabbit Road", anchor="w", font=("Arial", 10))
        self.canvas.create_rectangle(100, 80, 150, 100, fill="red")
        self.canvas.create_text(160, 90, text="Hanley Highway / Westway", anchor="w", font=("Arial", 10))

    def run(self):
        self.setup_window()
        self.draw_histogram()
        self.root.mainloop()


class TrafficAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Traffic Analysis System")
        self.root.geometry("600x500")

        tk.Label(self.root, text="Traffic Analysis System", font=("Arial", 16, "bold")).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Label(frame, text="Day:").grid(row=0, column=0, padx=5)
        tk.Label(frame, text="Month:").grid(row=0, column=2, padx=5)
        tk.Label(frame, text="Year:").grid(row=0, column=4, padx=5)

        self.day = tk.Spinbox(frame, from_=1, to=31, width=5)
        self.month = tk.Spinbox(frame, from_=1, to=12, width=5)
        self.year = tk.Spinbox(frame, from_=2000, to=2025, width=6)
        self.day.grid(row=0, column=1)
        self.month.grid(row=0, column=3)
        self.year.grid(row=0, column=5)

        tk.Button(self.root, text="Select CSV File", command=self.load_and_analyze).pack(pady=15)
        self.result_box = tk.Text(self.root, width=70, height=15, wrap="word")
        self.result_box.pack(padx=10, pady=10)

        tk.Button(self.root, text="Exit", command=self.root.quit, bg="red", fg="white").pack(pady=10)

        self.root.mainloop()

    def load_and_analyze(self):
        day, month, year = int(self.day.get()), int(self.month.get()), int(self.year.get())
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            messagebox.showinfo("Info", "No file selected.")
            return
        try:
            data = process_csv_data(file_path)
            outputs = display_outcomes(data, f"traffic_data{day:02d}{month:02d}{year}.csv")

            self.result_box.delete(1.0, tk.END)
            self.result_box.insert(tk.END, "Traffic Analysis Results:\n\n")
            for k, v in outputs.items():
                self.result_box.insert(tk.END, f"{k}: {v}\n")

            traffic_data = {"Elm Avenue/Rabbit Road": defaultdict(int), "Hanley Highway/Westway": defaultdict(int)}
            for row in data:
                hour = row["timeOfDay"].split(":")[0]
                traffic_data[row["JunctionName"]][hour] += 1

            HistogramApp(traffic_data, (day, month, year)).run()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze file: {e}")


if __name__ == "__main__":
    TrafficAnalysisApp()
