# Face-Recognition-Attendance-System-Using-OpenCV

A desktop application built with Python and Tkinter that automates student attendance using facial recognition technology.

## Features

- **Face Recognition**: Captures and recognizes student faces in real-time
- **Student Management**: 
  - Register new students with their details and facial data
  - Organize students by faculty and year
  - Manage student database entries
- **Attendance Tracking**:
  - Real-time attendance marking
  - Date-wise attendance records
  - Multiple faculty and year support
- **Reporting System**:
  - Generate daily attendance reports
  - Export monthly attendance summaries
  - Export attendance logs to CSV format

## Technical Details

- **Frontend**: Built with Tkinter for a user-friendly GUI
- **Backend**: SQLite database for data storage
- **Face Recognition**: OpenCV for face detection and recognition
- **Data Processing**: Pandas for report generation and data manipulation

## Requirements

- Python 3.x
- OpenCV
- Tkinter
- SQLite3
- Pandas
- tkcalendar

## Usage

1. Run the application: `python main.py`
2. Register students using the "Register New Person" button
3. Take attendance using the "Take Attendance" button
4. Generate reports and manage the database as needed

## Database Structure

- Separate tables for each faculty and year combination
- Stores student details and attendance records
- Automatically creates required directories and database tables

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

[Add your chosen license here]

# Face Recognition Attendance System - Technical Documentation

## Core Components and Workflow

### 1. Class Structure
The system is built around the `AttendanceSystemGUI` class, which handles all main functionalities:
- GUI management
- Face recognition
- Database operations
- Attendance tracking
- Report generation

### 2. Initialization Process
When the system starts:
- Creates necessary directories for database and photos
- Initializes SQLite database connection
- Sets up database tables for different faculties and years
- Loads existing face data from the photos directory
- Creates the GUI interface

### 3. Database Management
The system uses SQLite with two types of tables:
```
- Faculty_YearX_Students (stores student information)
  - id
  - name
  - roll_number
  - registration_date

- Faculty_YearX_Attendance (stores attendance records)
  - id
  - student_name
  - student_id
  - attendance_date
  - attendance_time
  - status
```

### 4. Face Recognition Process

#### Registration:
1. Captures multiple face samples (10 samples)
2. Converts images to grayscale
3. Detects face using Haar Cascade Classifier
4. Resizes face images to 200x200 pixels
5. Saves the average face as reference

#### Attendance:
1. Captures live video feed
2. Detects faces in each frame
3. Compares detected faces with stored faces
4. Uses template matching (TM_CCOEFF_NORMED) for comparison
5. Requires continuous recognition for 2 seconds (60 frames)
6. Marks attendance when recognition threshold is met

### 5. Key Functions

#### `register_new_person()`
- Creates registration window
- Collects student details
- Triggers face capture process
- Saves data to database

#### `capture_face()`
- Captures multiple face samples
- Processes and saves face data
- Updates database with new entry

#### `run_attendance()`
- Handles real-time face recognition
- Tracks recognition duration
- Marks attendance for recognized students
- Updates UI with recognition status

#### `mark_attendance()`
- Records attendance in database
- Updates attendance log
- Handles duplicate entries

### 6. Reporting System

#### Report Types:
- Daily Attendance Summary
- Monthly Attendance Report
- Exportable attendance logs

#### Export Formats:
- Excel (.xlsx) for detailed reports
- CSV for attendance logs

### 7. User Interface Components

#### Main Window:
- Left Panel: Control buttons and status
- Right Panel: Attendance records display

#### Additional Windows:
- Registration Form
- Report Generation
- Database Management
- Calendar Selection

## Flow of Operations

1. **Student Registration**:
   ```
   Input Details → Capture Face → Process Samples → Save to Database
   ```

2. **Attendance Taking**:
   ```
   Start Camera → Detect Face → Compare with Database → Mark Attendance
   ```

3. **Report Generation**:
   ```
   Select Date/Period → Query Database → Generate Report → Export
   ```

## Performance Considerations

- Face recognition uses a threshold of 0.5 for similarity matching
- Requires 60 frames of continuous recognition
- Uses grayscale processing for better performance
- Implements template matching for face comparison

## Error Handling

- Duplicate roll number detection
- Database connection management
- Camera access verification
- Face detection validation
- Data validation during registration

## Future Enhancement Possibilities

1. Multiple camera support
2. Advanced face recognition algorithms
3. Cloud database integration
4. Mobile app integration
5. Automatic email notifications
6. Attendance statistics and analytics
7. Batch processing for registration

This system provides a robust foundation for automated attendance tracking while maintaining flexibility for future improvements and modifications.
