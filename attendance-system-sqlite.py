import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import os
import sqlite3
from tkcalendar import Calendar
import csv

class AttendanceSystemGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x800")
        
        # Initialize OpenCV face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Database paths
        self.database_dir = "./student_database"
        self.photos_dir = os.path.join(self.database_dir, "photos")
       # self.details_file = os.path.join(self.database_dir, "student_details.csv")
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.photos_dir, exist_ok=True)
        
        
        '''# Create CSV file with headers if not exists
        if not os.path.exists(self.details_file):
            with open(self.details_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'ID', 'Faculty', 'Year'])
        '''
        
        # SQLite Database Setup
        self.conn = sqlite3.connect(os.path.join(self.database_dir, 'attendance_system.db'))
        self.cursor = self.conn.cursor()
        
        
        # Default faculties
        self.faculties = ['Civil', 'Computer', 'Mechanical', 'Electrical', 'Agriculture']
        self.years = [1, 2, 3, 4]
        
        # Create tables for students and attendance
        self.create_student_tables()
        self.create_attendance_tables()
        
        self.known_faces = {}
        self.attendance_log = []
        self.current_date = datetime.now().date()
        self.marked_today = set()
        
        self.load_database()
        self.setup_gui()    
    
    def create_student_tables(self):
        for faculty in self.faculties:
            for year in self.years:
                self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {faculty}_Year{year}_Students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll_number TEXT NOT NULL UNIQUE,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
        self.conn.commit()
    
    def create_attendance_tables(self):
        for faculty in self.faculties:
            for year in self.years:
                self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {faculty}_Year{year}_Attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    attendance_date DATE NOT NULL,
                    attendance_time DATETIME NOT NULL,
                    status TEXT DEFAULT 'Absent'
                )
                ''')
        self.conn.commit()
    
    def load_database(self):
        """Load all registered faces"""
        for filename in os.listdir(self.photos_dir):
            if filename.endswith('.jpg'):
                name = os.path.splitext(filename)[0]
                image_path = os.path.join(self.photos_dir, filename)
                self.known_faces[name] = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    def setup_gui(self):
        # Configure style

        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 24, 'bold'))
        style.configure('SubHeader.TLabel', font=('Arial', 14))
        style.configure('Action.TButton', font=('Arial', 12), padding=10)
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create left and right panels
        left_panel = ttk.Frame(self.main_container)
        right_panel = ttk.Frame(self.main_container)
        
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        self.main_container.grid_columnconfigure(1, weight=1)
        
        # Left Panel - Controls
        ttk.Label(left_panel, text="Controls", style='Header.TLabel').pack(pady=(0, 20))
        
        buttons = [
            ("Register New Person", self.register_new_person),
            ("Take Attendance", self.run_attendance),
            ("Export Attendance Log", self.export_attendance),
            ("Generate Reports", self.generate_reports),
            ("Manage Database", self.manage_database)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(left_panel, text=text, command=command, style='Action.TButton')
            btn.pack(fill='x', pady=5)
        
        # Status display
        self.status_label = ttk.Label(left_panel, text="Ready", style='SubHeader.TLabel')
        self.status_label.pack(pady=20)
        
        # Right Panel - Attendance Display
        ttk.Label(right_panel, text="Attendance Records", style='Header.TLabel').pack(pady=(0, 20))
        
        # Date filter
        filter_frame = ttk.Frame(right_panel)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Date: ").pack(side='left')
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
        date_entry.pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="Calendar", command=self.show_calendar).pack(side='left')
        ttk.Button(filter_frame, text="Refresh", command=self.refresh_attendance_table).pack(side='left', padx=5)
        
        # Create Treeview for attendance display
        self.setup_attendance_table(right_panel)
        
        # Initial table population
        self.refresh_attendance_table()
        
    def setup_attendance_table(self, parent):
    # Create Treeview with scrollbar
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(
            table_frame, 
            columns=('Name', 'ID', 'Faculty', 'Year', 'Time', 'Status'), 
            show='headings'
        )

        # Configure columns
        self.tree.heading('Name', text='Name')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Faculty', text='Faculty')
        self.tree.heading('Year', text='Year')
        self.tree.heading('Time', text='Time')
        self.tree.heading('Status', text='Status')

        self.tree.column('Name', width=100)
        self.tree.column('ID', width=80)
        self.tree.column('Faculty', width=80)
        self.tree.column('Year', width=50)
        self.tree.column('Time', width=100)
        self.tree.column('Status', width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        
    def refresh_attendance_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get selected date
        selected_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d').date()
        
    
        # Fetch student details from the database
        student_details = {}
        for faculty in self.faculties:
            for year in self.years:
                self.cursor.execute(f'''
                    SELECT name, roll_number, ? AS faculty, ? AS year 
                    FROM {faculty}_Year{year}_Students
                ''', (faculty, year))
                for row in self.cursor.fetchall():
                    student_details[row[0]] = {
                        'ID': row[1],
                        'Faculty': row[2],
                        'Year': row[3]
                    }
        
        # Filter attendance for selected date
        day_attendance = [log for log in self.attendance_log if log['date'] == selected_date]
        
        # Sort by time
        day_attendance.sort(key=lambda x: x['timestamp'])
        
        # Add to table
        
        for entry in day_attendance:
            # Get student details
            student_info = student_details.get(entry['name'], {})
            
            self.tree.insert('', 'end', values=(
                entry['name'],
                student_info.get('ID', 'N/A'),
                student_info.get('Faculty', 'N/A'),
                student_info.get('Year', 'N/A'),
                entry['timestamp'].strftime('%H:%M:%S'),
                'Present'
            ))    
    def show_calendar(self):
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal = Calendar(cal_window, selectmode='day')
        cal.pack(padx=10, pady=10)
        
        def set_date():
            self.date_var.set(cal.get_date())
            cal_window.destroy()
            self.refresh_attendance_table()
        
        ttk.Button(cal_window, text="Select", command=set_date).pack(pady=10)
    
    def generate_reports(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Reports")
        report_window.geometry("400x300")
        
        ttk.Label(report_window, text="Select Report Type", style='SubHeader.TLabel').pack(pady=20)
        
        reports = [
            ("Daily Attendance Summary", self.generate_daily_report),
            ("Monthly Attendance Report", self.generate_monthly_report)
            
        ]
        
        for text, command in reports:
            #ttk.Button(report_window, text=text, command=command).pack(pady=5)
             #CHANGEEEEEEE
             ttk.Button(report_window, text=text, command=lambda cmd=command: cmd()).pack(pady=5)
             ####################
    def manage_database(self):
        db_window = tk.Toplevel(self.root)
        db_window.title("Manage Database")
        db_window.geometry("600x400")
        
        # Create Treeview for registered users
        self.tree = ttk.Treeview(db_window, columns=('Name', 'Registration Date'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Registration Date', text='Registration Date')
        self.tree.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Populate with registered users
        for name in self.known_faces.keys():
            self.tree.insert('', 'end', values=(name, 'N/A'))
        
        # Control buttons
        btn_frame = ttk.Frame(db_window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Delete Selected", 
                  command=lambda: self.delete_person(self.tree.selection())).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Photo", 
                  command=lambda: self.update_person_photo(self.tree.selection())).pack(side='left', padx=5)
    
    def delete_person(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a person to delete")
            return
        
        name = self.tree.item(selection[0])['values'][0]
        '''if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            file_path = os.path.join(self.database_dir, f"{name}.jpg")
            if os.path.exists(file_path):
                os.remove(file_path)
                del self.known_faces[name]
                messagebox.showinfo("Success", f"Deleted {name} from database")
    ''' 
        #CHANGEEEEEE
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            # Delete the file and remove from known_faces
            file_path = os.path.join(self.photos_dir, f"{name}.jpg")
            if os.path.exists(file_path):
                os.remove(file_path)
            if name in self.known_faces:
                del self.known_faces[name]
            self.tree.delete(selection[0])  # Remove the item from the Treeview
            self.photos_dir.delete(f"{name}.jpg")
            messagebox.showinfo("Success", f"Deleted {name} from database")
        try:
            self.conn = sqlite3.connect("./student_database/attendance_system")  # Connect to the database
            self.cursor = self.conn.cursor()
            self.cursor.execute("DELETE FROM persons WHERE name = ?", (name,))
            self.conn.commit()
            self.conn.close()
            messagebox.showinfo("Success", f"Deleted {name} from database")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete {name} from database: {e}")    
        ####################################    
    def update_person_photo(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a person to update")
            return
        
        name = self.tree.item(selection[0])['values'][0]
        self.capture_face(name, update=True)
    
    def generate_daily_report(self):
        selected_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d').date()
        df = pd.DataFrame([log for log in self.attendance_log if log['date'] == selected_date])
        filename = f".//Reports//daily_report_{selected_date.strftime('%Y%m%d')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Daily report exported to {filename}")
    
    def generate_monthly_report(self):
        selected_month = datetime.strptime(self.date_var.get(), '%Y-%m').date()  # Format: YYYY-MM
        month_start = selected_month.replace(day=1)
        next_month_start = (month_start + timedelta(days=31)).replace(day=1)
        
        # Filter attendance logs for the selected month
        monthly_logs = [
            log for log in self.attendance_log 
            if month_start <= log['date'] < next_month_start
        ]
        if not monthly_logs:
            messagebox.showinfo("No Data", "No attendance records found for the selected month.")
            return
        
        df = pd.DataFrame(monthly_logs)
        filename = f".//Reports//monthly_report_{month_start.strftime('%Y%m')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Monthly report exported to {filename}")


            
    def register_new_person(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New Person")
        register_window.geometry("400x300")
        
        ttk.Label(register_window, text="Enter Name:").pack(pady=5)
        name_entry = ttk.Entry(register_window, font=('Arial', 12))
        name_entry.pack(pady=5)
        
        ttk.Label(register_window, text="Enter Roll Number:").pack(pady=5)
        id_entry = ttk.Entry(register_window, font=('Arial', 12))
        id_entry.pack(pady=5)
        
        ttk.Label(register_window, text="Select Faculty:").pack(pady=5)
        faculty_var = tk.StringVar(value=self.faculties[0])
        faculty_dropdown = ttk.Combobox(register_window, textvariable=faculty_var, values=self.faculties)
        faculty_dropdown.pack(pady=5)
        
        ttk.Label(register_window, text="Select Year:").pack(pady=5)
        year_var = tk.IntVar(value=1)
        year_dropdown = ttk.Combobox(register_window, textvariable=year_var, values=self.years)
        year_dropdown.pack(pady=5)
    
        def start_capture():
            name = name_entry.get().strip()
            student_id = id_entry.get().strip()
            faculty = faculty_var.get()
            year = year_var.get()
            
            if not all([name, student_id, faculty]):
                messagebox.showerror("Error", "Please fill all details")
                return
            
            # Check for duplicate roll number in the same faculty and year
            self.cursor.execute(f'''
                SELECT * FROM {faculty}_Year{year}_Students 
                WHERE roll_number = ?
            ''', (student_id,))
            
            if self.cursor.fetchone():
                messagebox.showerror("Error", f"Roll number {student_id} already exists")
                return
            
            # Insert student details into specific faculty and year table
            self.cursor.execute(f'''
                INSERT INTO {faculty}_Year{year}_Students 
                (name, roll_number) VALUES (?, ?)
            ''', (name, student_id))
            self.conn.commit()
            
            register_window.destroy()
            self.capture_face(name, student_id, faculty, year)
        
        ttk.Button(register_window, text="Start Capture", command=start_capture).pack(pady=10)

    def capture_face(self, name, student_id, faculty, year):
        # Save face photos in photos_dir
        photo_path = os.path.join(self.photos_dir, f"{name}.jpg")
        
        cap = cv2.VideoCapture(1)
        face_samples = []
        sample_count = 0
        required_samples = 10
        
        while sample_count < required_samples:
            ret, frame = cap.read()
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.putText(frame, f"Capturing face {sample_count+1}/{required_samples}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'c' to capture or 'q' to quit", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Register Face', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and len(faces) > 0:
                x, y, w, h = faces[0]
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (200, 200))
                face_samples.append(face)
                
                cv2.imwrite(photo_path, face)
                
                sample_count += 1
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if face_samples:
           # self.known_faces[name] = face_samples[0]
           #CHANGEEEEEEEEEEEEEEEE
             # Save student details
            average_face = np.mean(face_samples, axis=0).astype(np.uint8)
            cv2.imwrite(photo_path, average_face)
            self.known_faces[name] = average_face 
            messagebox.showinfo("Success", f"Successfully registered {name}")
            ##############################
    def compare_faces(self, face1, face2):
        """Compare two faces using template matching"""
        face1 = cv2.resize(face1, (200, 200))
        face2 = cv2.resize(face2, (200, 200))
        
        # Use template matching to compare faces
        result = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)[0][0]
        return result
    
    def run_attendance(self):
        self.status_label.config(text="Taking attendance... Press 'q' to quit")
        cap = cv2.VideoCapture(1)

        presence_duration = {}  # Track recognition duration for each person
        required_frames = 60  # Assuming 60 FPS, 2 seconds = 60 frames

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]

                # Compare with known faces
                max_similarity = 0
                recognized_name = "Unknown"

                for name, known_face in self.known_faces.items():
                    similarity = self.compare_faces(face, known_face)
                    if similarity > max_similarity and similarity > 0.5:
                        max_similarity = similarity
                        recognized_name = name

                # Update presence duration
                if recognized_name != "Unknown":
                    if recognized_name in presence_duration:
                        presence_duration[recognized_name] += 1
                    else:
                        presence_duration[recognized_name] = 1

                    # Mark attendance if recognized for required frames
                    if presence_duration[recognized_name] >= required_frames and recognized_name not in self.marked_today:
                        self.mark_attendance(recognized_name)
                
                # Reset presence duration for unrecognized faces
                else:
                    for name in list(presence_duration.keys()):
                        if name not in self.marked_today:
                            presence_duration[name] = 0

                # Draw rectangle and name
                color = (0, 255, 0) if recognized_name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

                # Show status
                status = "Marked" if recognized_name in self.marked_today else "Not Marked"
                cv2.putText(frame, f"{recognized_name} - {status}",
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, color, 2)

            cv2.imshow('Attendance System', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.status_label.config(text="Ready")



    def mark_attendance(self, name):
        # Retrieve student details
        for faculty in self.faculties:
            for year in self.years:
                self.cursor.execute(f'''
                    SELECT roll_number FROM {faculty}_Year{year}_Students 
                    WHERE name = ?
                ''', (name,))
                result = self.cursor.fetchone()
                
                if result:
                    student_id = result[0]
                    timestamp = datetime.now()
                    
                    # Insert attendance record
                    self.cursor.execute(f'''
                        INSERT INTO {faculty}_Year{year}_Attendance 
                        (student_name, student_id, attendance_date, attendance_time) 
                        VALUES (?, ?, ?, ?)
                    ''', (name, student_id, timestamp.date(), timestamp))
                    self.conn.commit()
                    break

        self.attendance_log.append({
            'name': name,
            'timestamp': timestamp,
            'date': timestamp.date()
        })
        self.marked_today.add(name)
        self.status_label.config(text=f"Marked attendance for {name}")
    def view_attendance(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Today's Attendance")
        view_window.geometry("400x400")
        
        text_widget = tk.Text(view_window, font=('Arial', 12), wrap=tk.WORD)
        text_widget.pack(expand=True, fill='both', padx=20, pady=20)
        
        today = datetime.now().date()
        today_attendance = [log for log in self.attendance_log if log['date'] == today]
        
        if today_attendance:
            text_widget.insert('end', "Today's Attendance:\n\n")
            for entry in today_attendance:
                text_widget.insert('end', 
                                 f"{entry['name']}: {entry['timestamp'].strftime('%H:%M:%S')}\n")
        else:
            text_widget.insert('end', "No attendance records for today")
        
        text_widget.config(state='disabled')    

    def export_attendance(self):
        filename = f"attendance_log_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Collect attendance from all faculty and year tables
        all_attendance = []
        for faculty in self.faculties:
            for year in self.years:
                self.cursor.execute(f'''
                    SELECT * FROM {faculty}_Year{year}_Attendance
                ''')
                all_attendance.extend(self.cursor.fetchall())
        
        # Convert to DataFrame and export
        df = pd.DataFrame(all_attendance, columns=['ID', 'Name', 'Student ID', 'Date', 'Time', 'Status'])
        df.to_csv(filename, index=False)
        messagebox.showinfo("Success", f"Attendance exported to {filename}")

    def __del__(self):
        # Close database connection
        if hasattr(self, 'conn'):
            self.conn.close()

    # Rest of the methods remain unchanged from the original code
    # ... (setup_gui, refresh_attendance_table, etc.)

# The rest of the code remains the same as in the original file
def main():
    root = tk.Tk()
    app = AttendanceSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
