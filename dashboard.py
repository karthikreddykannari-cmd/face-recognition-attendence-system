import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import attendance
import os
import csv
from datetime import datetime
from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from PIL import Image, ImageTk


class AttendanceDashboard:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Face Recognition Attendance System"
        )

        self.root.geometry(
            "1150x850"
        )

        self.root.configure(
            bg="#f4f6f8"
        )

        # =========================
        # TITLE
        # =========================

        tk.Label(
            root,
            text="Face Recognition Attendance System",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8"
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            root,
            text="Smart Attendance Dashboard",
            font=("Arial", 11),
            bg="#f4f6f8"
        ).pack(
            pady=(0, 15)
        )

        # =========================
        # STATISTICS
        # =========================

        stats_frame = tk.Frame(
            root,
            bg="#f4f6f8"
        )

        stats_frame.pack(
            fill="x",
            padx=25
        )

        self.total_label = self.create_card(
            stats_frame,
            "TOTAL STUDENTS",
            "0"
        )

        self.present_label = self.create_card(
            stats_frame,
            "PRESENT TODAY",
            "0"
        )

        self.absent_label = self.create_card(
            stats_frame,
            "ABSENT TODAY",
            "0"
        )

        self.days_label = self.create_card(
            stats_frame,
            "ATTENDANCE DAYS",
            "0"
        )

        # =========================
        # NOTEBOOK
        # =========================

        notebook = ttk.Notebook(
            root
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # Main attendance tab

        self.attendance_tab = tk.Frame(
            notebook,
            bg="#f4f6f8"
        )

        notebook.add(
            self.attendance_tab,
            text="Attendance Dashboard"
        )

        # Unknown faces tab

        self.unknown_tab = tk.Frame(
            notebook,
            bg="#f4f6f8"
        )

        notebook.add(
            self.unknown_tab,
            text="Unknown Faces"
        )

        # Build both tabs

        self.build_attendance_tab()

        self.build_unknown_faces_tab()

        # Initial refresh

        self.refresh_dashboard()

        self.refresh_unknown_faces()

    # =========================================================
    # CREATE CARD
    # =========================================================

    def create_card(
        self,
        parent,
        title,
        value
    ):

        card = tk.Frame(
            parent,
            bg="white",
            bd=1,
            relief="solid",
            height=100
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        card.pack_propagate(
            False
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 9, "bold"),
            bg="white"
        ).pack(
            pady=(15, 3)
        )

        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 22, "bold"),
            bg="white"
        )

        value_label.pack()

        return value_label

    # =========================================================
    # BUILD ATTENDANCE TAB
    # =========================================================

    def build_attendance_tab(self):

        # =========================
        # FILTER
        # =========================

        filter_frame = tk.Frame(
            self.attendance_tab,
            bg="#f4f6f8"
        )

        filter_frame.pack(
            fill="x",
            padx=5,
            pady=10
        )

        tk.Label(
            filter_frame,
            text="Search:",
            font=("Arial", 11, "bold"),
            bg="#f4f6f8"
        ).pack(
            side="left"
        )

        self.search_entry = tk.Entry(
            filter_frame,
            width=22,
            font=("Arial", 11)
        )

        self.search_entry.pack(
            side="left",
            padx=8
        )

        tk.Label(
            filter_frame,
            text="Date:",
            font=("Arial", 11, "bold"),
            bg="#f4f6f8"
        ).pack(
            side="left",
            padx=(15, 5)
        )

        self.date_entry = tk.Entry(
            filter_frame,
            width=15,
            font=("Arial", 11)
        )

        self.date_entry.insert(
            0,
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        self.date_entry.pack(
            side="left",
            padx=5
        )

        tk.Button(
            filter_frame,
            text="Apply Filter",
            command=self.apply_filter
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            filter_frame,
            text="Clear",
            command=self.clear_filter
        ).pack(
            side="left",
            padx=5
        )

        # =========================
        # MAIN BUTTONS
        # =========================

        button_frame = tk.Frame(
            self.attendance_tab,
            bg="#f4f6f8"
        )

        button_frame.pack(
            pady=5
        )

        tk.Button(
            button_frame,
            text="Start Recognition",
            width=18,
            command=self.start_recognition
        ).grid(
            row=0,
            column=0,
            padx=6
        )

        tk.Button(
            button_frame,
            text="Register Person",
            width=18,
            command=self.register_person
        ).grid(
            row=0,
            column=1,
            padx=6
        )

        tk.Button(
            button_frame,
            text="Refresh Dashboard",
            width=18,
            command=self.refresh_dashboard
        ).grid(
            row=0,
            column=2,
            padx=6
        )

        # =========================
        # EXPORT BUTTONS
        # =========================

        export_frame = tk.Frame(
            self.attendance_tab,
            bg="#f4f6f8"
        )

        export_frame.pack(
            pady=8
        )

        tk.Button(
            export_frame,
            text="Export CSV",
            width=18,
            command=self.export_csv
        ).grid(
            row=0,
            column=0,
            padx=6
        )

        tk.Button(
            export_frame,
            text="Export Excel",
            width=18,
            command=self.export_excel
        ).grid(
            row=0,
            column=1,
            padx=6
        )

        tk.Button(
            export_frame,
            text="Generate PDF",
            width=18,
            command=self.export_pdf
        ).grid(
            row=0,
            column=2,
            padx=6
        )

        # =========================
        # ATTENDANCE RECORDS
        # =========================

        tk.Label(
            self.attendance_tab,
            text="Attendance Records",
            font=("Arial", 14, "bold"),
            bg="#f4f6f8"
        ).pack(
            anchor="w",
            padx=5,
            pady=(10, 5)
        )

        table_frame = tk.Frame(
            self.attendance_tab,
            bg="white"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=5
        )

        columns = (
            "Name",
            "Date",
            "Time"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading(
            "Name",
            text="Name"
        )

        self.table.heading(
            "Date",
            text="Date"
        )

        self.table.heading(
            "Time",
            text="Time"
        )

        self.table.column(
            "Name",
            width=350
        )

        self.table.column(
            "Date",
            width=200
        )

        self.table.column(
            "Time",
            width=200
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # =========================
        # ANALYTICS
        # =========================

        tk.Label(
            self.attendance_tab,
            text="Attendance Analytics",
            font=("Arial", 14, "bold"),
            bg="#f4f6f8"
        ).pack(
            anchor="w",
            padx=5,
            pady=(15, 5)
        )

        analytics_frame = tk.Frame(
            self.attendance_tab,
            bg="white"
        )

        analytics_frame.pack(
            fill="x",
            padx=5,
            pady=(0, 10)
        )

        analytics_columns = (
            "Student",
            "Present Days",
            "Total Days",
            "Attendance"
        )

        self.analytics_table = ttk.Treeview(
            analytics_frame,
            columns=analytics_columns,
            show="headings",
            height=4
        )

        for column in analytics_columns:

            self.analytics_table.heading(
                column,
                text=column
            )

        self.analytics_table.column(
            "Student",
            width=350
        )

        self.analytics_table.column(
            "Present Days",
            width=180
        )

        self.analytics_table.column(
            "Total Days",
            width=180
        )

        self.analytics_table.column(
            "Attendance",
            width=180
        )

        self.analytics_table.pack(
            fill="x"
        )

    # =========================================================
    # UNKNOWN FACES TAB
    # =========================================================

    def build_unknown_faces_tab(self):

        # =========================
        # TITLE
        # =========================

        tk.Label(
            self.unknown_tab,
            text="Unknown Face Detection",
            font=("Arial", 18, "bold"),
            bg="#f4f6f8"
        ).pack(
            pady=(15, 3)
        )

        tk.Label(
            self.unknown_tab,
            text=(
                "Captured faces that were not matched "
                "with registered students"
            ),
            font=("Arial", 10),
            bg="#f4f6f8"
        ).pack(
            pady=(0, 10)
        )

        # =========================
        # BUTTONS
        # =========================

        button_frame = tk.Frame(
            self.unknown_tab,
            bg="#f4f6f8"
        )

        button_frame.pack(
            pady=5
        )

        tk.Button(
            button_frame,
            text="Refresh Unknown Faces",
            width=22,
            command=self.refresh_unknown_faces
        ).grid(
            row=0,
            column=0,
            padx=6
        )

        tk.Button(
            button_frame,
            text="Open Selected Image",
            width=22,
            command=self.open_selected_unknown
        ).grid(
            row=0,
            column=1,
            padx=6
        )

        tk.Button(
            button_frame,
            text="Delete Selected",
            width=22,
            command=self.delete_selected_unknown
        ).grid(
            row=0,
            column=2,
            padx=6
        )

        # =========================
        # UNKNOWN COUNT
        # =========================

        self.unknown_count_label = tk.Label(
            self.unknown_tab,
            text="Unknown Faces: 0",
            font=("Arial", 12, "bold"),
            bg="#f4f6f8"
        )

        self.unknown_count_label.pack(
            pady=8
        )

        # =========================
        # LIST
        # =========================

        list_frame = tk.Frame(
            self.unknown_tab,
            bg="white"
        )

        list_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        columns = (
            "File",
            "Date",
            "Time"
        )

        self.unknown_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings"
        )

        self.unknown_tree.heading(
            "File",
            text="Image"
        )

        self.unknown_tree.heading(
            "Date",
            text="Date"
        )

        self.unknown_tree.heading(
            "Time",
            text="Time"
        )

        self.unknown_tree.column(
            "File",
            width=500
        )

        self.unknown_tree.column(
            "Date",
            width=200
        )

        self.unknown_tree.column(
            "Time",
            width=200
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.unknown_tree.yview
        )

        self.unknown_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.unknown_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Double-click to open

        self.unknown_tree.bind(
            "<Double-1>",
            lambda event: self.open_selected_unknown()
        )

    # =========================================================
    # START RECOGNITION
    # =========================================================

    def start_recognition(self):

        subprocess.Popen([
            sys.executable,
            "main.py"
        ])

    # =========================================================
    # REGISTER PERSON
    # =========================================================

    def register_person(self):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Register Person"
        )

        window.geometry(
            "350x180"
        )

        tk.Label(
            window,
            text="Enter Name:",
            font=("Arial", 12)
        ).pack(
            pady=15
        )

        name_entry = tk.Entry(
            window,
            width=30
        )

        name_entry.pack()

        def register():

            name = name_entry.get().strip()

            if not name:

                messagebox.showwarning(
                    "Warning",
                    "Please enter a name."
                )

                return

            subprocess.Popen([
                sys.executable,
                "register.py",
                "--name",
                name,
                "--webcam"
            ])

            window.destroy()

        tk.Button(
            window,
            text="Open Camera",
            command=register
        ).pack(
            pady=20
        )

    # =========================================================
    # REFRESH DASHBOARD
    # =========================================================

    def refresh_dashboard(self):

        self.load_attendance()

        self.update_statistics()

        self.update_analytics()

    # =========================================================
    # LOAD ATTENDANCE
    # =========================================================

    def load_attendance(
        self,
        search="",
        date=""
    ):

        for item in self.table.get_children():

            self.table.delete(
                item
            )

        rows = attendance.database.get_attendance()

        for name, row_date, time in rows:

            if search:

                if search.lower() not in name.lower():

                    continue

            if date:

                if row_date != date:

                    continue

            self.table.insert(
                "",
                "end",
                values=(
                    name,
                    row_date,
                    time
                )
            )

    # =========================================================
    # APPLY FILTER
    # =========================================================

    def apply_filter(self):

        search = self.search_entry.get().strip()

        date = self.date_entry.get().strip()

        self.load_attendance(
            search,
            date
        )

    # =========================================================
    # CLEAR FILTER
    # =========================================================

    def clear_filter(self):

        self.search_entry.delete(
            0,
            tk.END
        )

        self.date_entry.delete(
            0,
            tk.END
        )

        self.load_attendance()

    # =========================================================
    # STATISTICS
    # =========================================================

    def update_statistics(self):

        known_faces_path = "known_faces"

        if os.path.exists(
            known_faces_path
        ):

            students = [
                file
                for file in os.listdir(
                    known_faces_path
                )
                if file.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png"
                    )
                )
            ]

            total_students = len(
                students
            )

        else:

            total_students = 0

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        rows = attendance.database.get_attendance()

        present_students = set()

        dates = set()

        for name, date, time in rows:

            dates.add(
                date
            )

            if date == today:

                present_students.add(
                    name
                )

        present_today = len(
            present_students
        )

        absent_today = max(
            total_students -
            present_today,
            0
        )

        total_days = len(
            dates
        )

        self.total_label.config(
            text=str(
                total_students
            )
        )

        self.present_label.config(
            text=str(
                present_today
            )
        )

        self.absent_label.config(
            text=str(
                absent_today
            )
        )

        self.days_label.config(
            text=str(
                total_days
            )
        )

    # =========================================================
    # ANALYTICS
    # =========================================================

    def update_analytics(self):

        for item in self.analytics_table.get_children():

            self.analytics_table.delete(
                item
            )

        known_faces_path = "known_faces"

        students = []

        if os.path.exists(
            known_faces_path
        ):

            for file in os.listdir(
                known_faces_path
            ):

                if file.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png"
                    )
                ):

                    name = os.path.splitext(
                        file
                    )[0]

                    students.append(
                        name
                    )

        rows = attendance.database.get_attendance()

        all_dates = set()

        attendance_count = {}

        for name, date, time in rows:

            all_dates.add(
                date
            )

            if name not in attendance_count:

                attendance_count[name] = set()

            attendance_count[name].add(
                date
            )

        total_days = len(
            all_dates
        )

        for student in students:

            present_days = len(
                attendance_count.get(
                    student,
                    set()
                )
            )

            if total_days > 0:

                percentage = (
                    present_days /
                    total_days
                ) * 100

            else:

                percentage = 0

            self.analytics_table.insert(
                "",
                "end",
                values=(
                    student,
                    present_days,
                    total_days,
                    f"{percentage:.1f}%"
                )
            )

    # =========================================================
    # GET ATTENDANCE
    # =========================================================

    def get_all_attendance(self):

        return attendance.database.get_attendance()

    # =========================================================
    # EXPORT CSV
    # =========================================================

    def export_csv(self):

        rows = self.get_all_attendance()

        if not rows:

            messagebox.showinfo(
                "Export CSV",
                "No attendance records available."
            )

            return

        filename = (
            "attendance_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".csv"
        )

        filepath = os.path.join(
            os.getcwd(),
            filename
        )

        try:

            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(
                    file
                )

                writer.writerow([
                    "Name",
                    "Date",
                    "Time"
                ])

                writer.writerows(
                    rows
                )

            messagebox.showinfo(
                "Export Successful",
                f"CSV file created:\n\n{filepath}"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # =========================================================
    # EXPORT EXCEL
    # =========================================================

    def export_excel(self):

        rows = self.get_all_attendance()

        if not rows:

            messagebox.showinfo(
                "Export Excel",
                "No attendance records available."
            )

            return

        filename = (
            "attendance_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".xlsx"
        )

        filepath = os.path.join(
            os.getcwd(),
            filename
        )

        try:

            workbook = Workbook()

            sheet = workbook.active

            sheet.title = "Attendance"

            sheet.append([
                "Name",
                "Date",
                "Time"
            ])

            for row in rows:

                sheet.append(
                    row
                )

            sheet.column_dimensions[
                "A"
            ].width = 30

            sheet.column_dimensions[
                "B"
            ].width = 18

            sheet.column_dimensions[
                "C"
            ].width = 18

            workbook.save(
                filepath
            )

            messagebox.showinfo(
                "Export Successful",
                f"Excel file created:\n\n{filepath}"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # =========================================================
    # EXPORT PDF
    # =========================================================

    def export_pdf(self):

        rows = self.get_all_attendance()

        if not rows:

            messagebox.showinfo(
                "Export PDF",
                "No attendance records available."
            )

            return

        filename = (
            "attendance_report_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".pdf"
        )

        filepath = os.path.join(
            os.getcwd(),
            filename
        )

        try:

            known_faces_path = "known_faces"

            students = []

            if os.path.exists(
                known_faces_path
            ):

                for file in os.listdir(
                    known_faces_path
                ):

                    if file.lower().endswith(
                        (
                            ".jpg",
                            ".jpeg",
                            ".png"
                        )
                    ):

                        name = os.path.splitext(
                            file
                        )[0]

                        students.append(
                            name
                        )

            all_dates = set()

            attendance_count = {}

            for name, date, time in rows:

                all_dates.add(
                    date
                )

                if name not in attendance_count:

                    attendance_count[name] = set()

                attendance_count[name].add(
                    date
                )

            total_days = len(
                all_dates
            )

            document = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=15 * mm,
                leftMargin=15 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm
            )

            styles = getSampleStyleSheet()

            elements = []

            elements.append(
                Paragraph(
                    "Face Recognition Attendance Report",
                    styles["Title"]
                )
            )

            elements.append(
                Spacer(
                    1,
                    8
                )
            )

            elements.append(
                Paragraph(
                    "Generated on: "
                    + datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    ),
                    styles["Normal"]
                )
            )

            elements.append(
                Paragraph(
                    f"Total Students: {len(students)}",
                    styles["Normal"]
                )
            )

            elements.append(
                Paragraph(
                    f"Total Attendance Days: {total_days}",
                    styles["Normal"]
                )
            )

            elements.append(
                Spacer(
                    1,
                    15
                )
            )

            data = [[
                "Student",
                "Present Days",
                "Total Days",
                "Attendance %"
            ]]

            for student in students:

                present_days = len(
                    attendance_count.get(
                        student,
                        set()
                    )
                )

                percentage = (
                    present_days /
                    total_days *
                    100
                    if total_days > 0
                    else 0
                )

                data.append([
                    student,
                    str(present_days),
                    str(total_days),
                    f"{percentage:.1f}%"
                ])

            table = Table(
                data,
                colWidths=[
                    75 * mm,
                    35 * mm,
                    30 * mm,
                    35 * mm
                ]
            )

            table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.grey
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER"
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.lightgrey
                        ]
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    )
                ])
            )

            elements.append(
                table
            )

            elements.append(
                Spacer(
                    1,
                    20
                )
            )

            elements.append(
                Paragraph(
                    "Attendance Records",
                    styles["Heading2"]
                )
            )

            elements.append(
                Spacer(
                    1,
                    8
                )
            )

            record_data = [[
                "Name",
                "Date",
                "Time"
            ]]

            for row in rows:

                record_data.append(
                    list(row)
                )

            record_table = Table(
                record_data,
                colWidths=[
                    90 * mm,
                    45 * mm,
                    35 * mm
                ]
            )

            record_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.grey
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.lightgrey
                        ]
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER"
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ])
            )

            elements.append(
                record_table
            )

            document.build(
                elements
            )

            messagebox.showinfo(
                "PDF Created",
                f"PDF report created successfully:\n\n{filepath}"
            )

        except Exception as e:

            messagebox.showerror(
                "PDF Export Error",
                str(e)
            )

    # =========================================================
    # UNKNOWN FACE HELPERS
    # =========================================================

    def get_unknown_faces(self):

        unknown_dir = "unknown_faces"

        if not os.path.exists(
            unknown_dir
        ):

            os.makedirs(
                unknown_dir,
                exist_ok=True
            )

        files = []

        for filename in os.listdir(
            unknown_dir
        ):

            if filename.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png"
                )
            ):

                filepath = os.path.join(
                    unknown_dir,
                    filename
                )

                files.append(
                    filepath
                )

        # Newest files first

        files.sort(
            key=os.path.getmtime,
            reverse=True
        )

        return files

    # =========================================================
    # REFRESH UNKNOWN FACES
    # =========================================================

    def refresh_unknown_faces(self):

        for item in self.unknown_tree.get_children():

            self.unknown_tree.delete(
                item
            )

        files = self.get_unknown_faces()

        for filepath in files:

            filename = os.path.basename(
                filepath
            )

            modified_time = datetime.fromtimestamp(
                os.path.getmtime(
                    filepath
                )
            )

            date = modified_time.strftime(
                "%Y-%m-%d"
            )

            time = modified_time.strftime(
                "%H:%M:%S"
            )

            self.unknown_tree.insert(
                "",
                "end",
                values=(
                    filename,
                    date,
                    time
                ),
                tags=(
                    filepath,
                )
            )

        self.unknown_count_label.config(
            text=f"Unknown Faces: {len(files)}"
        )

    # =========================================================
    # GET SELECTED UNKNOWN IMAGE
    # =========================================================

    def get_selected_unknown(self):

        selected = (
            self.unknown_tree.selection()
        )

        if not selected:

            return None

        item = selected[0]

        filename = self.unknown_tree.item(
            item,
            "values"
        )[0]

        filepath = os.path.join(
            "unknown_faces",
            filename
        )

        if not os.path.exists(
            filepath
        ):

            return None

        return filepath

    # =========================================================
    # OPEN SELECTED UNKNOWN IMAGE
    # =========================================================

    def open_selected_unknown(self):

        filepath = self.get_selected_unknown()

        if not filepath:

            messagebox.showwarning(
                "No Image Selected",
                "Please select an unknown face first."
            )

            return

        try:

            # Windows

            if sys.platform.startswith(
                "win"
            ):

                os.startfile(
                    os.path.abspath(
                        filepath
                    )
                )

            # macOS

            elif sys.platform == "darwin":

                subprocess.Popen([
                    "open",
                    filepath
                ])

            # Linux

            else:

                subprocess.Popen([
                    "xdg-open",
                    filepath
                ])

        except Exception as e:

            messagebox.showerror(
                "Open Image Error",
                str(e)
            )

    # =========================================================
    # DELETE SELECTED UNKNOWN IMAGE
    # =========================================================

    def delete_selected_unknown(self):

        filepath = self.get_selected_unknown()

        if not filepath:

            messagebox.showwarning(
                "No Image Selected",
                "Please select an unknown face first."
            )

            return

        filename = os.path.basename(
            filepath
        )

        confirm = messagebox.askyesno(
            "Delete Unknown Face",
            f"Delete this image?\n\n{filename}"
        )

        if not confirm:

            return

        try:

            os.remove(
                filepath
            )

            self.refresh_unknown_faces()

            messagebox.showinfo(
                "Deleted",
                "Unknown face image deleted."
            )

        except Exception as e:

            messagebox.showerror(
                "Delete Error",
                str(e)
            )


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AttendanceDashboard(
        root
    )

    root.mainloop()