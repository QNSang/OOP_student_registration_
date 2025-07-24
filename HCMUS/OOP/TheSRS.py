import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json


# ============= CORE CLASSES (Same as before) =============

class CourseSystemException(Exception):
    """Base exception for course system errors."""
    pass


class EnrollmentException(CourseSystemException):
    """Exception raised for enrollment-related errors."""
    pass


class SectionNotFoundException(CourseSystemException):
    """Exception raised when a section is not found."""
    pass


class Course:
    def __init__(self, courseNo: str, courseName: str, credits: int):
        if not courseNo or not courseName:  # Dùng raise valueError để chặn dữ liệu sai
            raise ValueError("Course number and course name cannot be empty")
        if credits <= 0:
            raise ValueError("Credits cannot be less than zero")

        self.__courseNo = courseNo
        self.__courseName = courseName
        self.__credits = credits
        self.__prerequisites: List['Course'] = []
        self.__sections: List['Section'] = []

    def scheduleOfSection(self, sectionNo: str, dayOfWeek: str, timeOfDay: str, room: str,
                          seatingCapacity: int) -> 'Section':
        if seatingCapacity <= 0:
            raise ValueError("Seating capacity must be positive")

        section = Section(sectionNo, dayOfWeek, timeOfDay, room, seatingCapacity)
        section.setCourse(self)
        self.__sections.append(section)
        return section

    def addPrerequisites(self, prerequisite: 'Course'):
        if prerequisite not in self.__prerequisites:
            self.__prerequisites.append(prerequisite)

    def hasPrerequisites(self) -> bool:
        return len(self.__prerequisites) > 0

    # getter
    def getPrerequisites(self) -> List['Course']:
        return self.__prerequisites.copy()

    def getCourseNo(self) -> str:
        return self.__courseNo

    def getCourseName(self) -> str:
        return self.__courseName

    def getCredits(self) -> int:
        return self.__credits

    def getSections(self) -> List['Section']:  # Fixed method name
        return self.__sections.copy()

    # display dùng str cho streamlit sau này
    def __str__(self) -> str:
        return f"{self.__courseNo} - {self.__courseName} ({self.__credits} credits)"  # Fixed variable names


class Section:
    def __init__(self, sectionNo: str, dayOfWeek: str, timeOfDay: str, room: str, seatingCapacity: int):
        if not sectionNo or not room:
            raise ValueError("Section number and room cannot be empty")
        if seatingCapacity <= 0:
            raise ValueError("Seating capacity must be positive")

        self.__sectionNo = sectionNo
        self.__dayOfWeek = dayOfWeek
        self.__timeOfDay = timeOfDay
        self.__room = room
        self.__seatingCapacity = seatingCapacity

        self.__course: Optional['Course'] = None
        self.__students: List['Student'] = []
        self.__professor: Optional['Professor'] = None

    def postGrade(self, student: 'Student', grade: str):
        if student not in self.__students:
            raise ValueError("Student not in the section")
        transcript = student.getTranscript()
        transcript.addEntry(self, grade)

    def confirmSeatAvailability(self) -> bool:
        return len(self.__students) < self.__seatingCapacity

    def enroll(self, student: 'Student') -> tuple[bool, str]:
        """Returns (success, message)"""
        try:
            if not self.confirmSeatAvailability():
                return False, "Section is full"
            if self.__course and self.__course.hasPrerequisites():
                prerequisites = self.__course.getPrerequisites()
                transcript = student.getTranscript()
                for course in prerequisites:
                    grade = transcript.getGrade(course.getCourseNo())
                    if grade is None:
                        return False, f"Missing prerequisite: {course.getCourseNo()}"  # Fixed method name
                    if float(grade) < 5.0:
                        return False, f"Low grade for prerequisite {course.getCourseNo()}: {grade}"  # Fixed method name

            self.__students.append(student)
            student.attendSection(self)
            return True, "Enrollment successful"

        except Exception as e:
            return False, str(e)

    # getter & setter
    def getSectionNo(self):
        return self.__sectionNo

    def getDayOfWeek(self):
        return self.__dayOfWeek

    def getTimeOfDay(self):
        return self.__timeOfDay

    def getRoom(self):
        return self.__room

    def getCourse(self):
        return self.__course

    def getCapacity(self):
        return self.__seatingCapacity

    def setCourse(self, course):
        self.__course = course

    def getStudents(self):
        return self.__students.copy()

    def setProfessor(self, professor):
        self.__professor = professor

    def getProfessor(self):
        return self.__professor

    def getEnrolledCount(self) -> int:  # Fixed method name
        return len(self.__students)

    def __str__(self) -> str:
        course_name = self.__course.getCourseName() if self.__course else "Unknown"
        return f"{self.__sectionNo} - {course_name}"


class Person(ABC):
    def __init__(self, name: str, ssn: str):
        if not name or not ssn:
            raise ValueError("Person name and SSN cannot be empty")
        self.name = name
        self.ssn = ssn

    @abstractmethod
    def display(self):
        pass


class Student(Person):
    def __init__(self, name: str, ssn: str, major: str, degree: str):
        super().__init__(name, ssn)
        if not major or not degree:
            raise ValueError("Student name and major and degree cannot be empty")
        self.__major = major
        self.__degree = degree
        self.__sections: List['Section'] = []
        self.__Transcript = Transcript()

    # getter & seter
    def getMajor(self) -> str:
        return self.__major

    def getDegree(self) -> str:
        return self.__degree

    def getSections(self) -> List['Section']:
        return self.__sections.copy()

    def setMajor(self, major):
        self.__major = major

    def setDegree(self, degree):
        self.__degree = degree

    def getTranscript(self):
        return self.__Transcript

    def attendSection(self, section: 'Section'):
        if section not in self.__sections:
            self.__sections.append(section)

    def dropSection(self, section):
        if section in self.__sections:
            self.__sections.remove(section)
            return True
        return False

    def display(self):
        pass

    def __str__(self) -> str:
        return f"{self.name} ({self.ssn}) - {self.__major}, {self.__degree}"


class Professor(Person):
    def __init__(self, name: str, ssn: str, title: str, department: str):
        super().__init__(name, ssn)
        if not title or not department:
            raise ValueError("Professor name and department cannot be empty")
        self.__title = title
        self.__department = department
        self.__sections: List['Section'] = []

    # getter & setter
    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title

    def getDepartment(self):
        return self.__department

    def setDepartment(self, department):
        self.__department = department

    def getSections(self):
        return self.__sections.copy()

    def agreeToTeach(self, section):
        if section not in self.__sections:
            self.__sections.append(section)
            section.setProfessor(self)

    def display(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__title} {self.name} - {self.__department}"


class TranscriptEntry:
    def __init__(self, section: 'Section', grade: str):
        self.__section = section
        self.__grade = grade

    # getter & setter
    def getGrade(self):
        return self.__grade

    def getSection(self):
        return self.__section

    def setGrade(self, grade):
        self.__grade = grade

    def setSection(self, section):
        self.__section = section


class Transcript:
    """Manager a student's academic transcript."""

    def __init__(self):
        self.__entries: Dict[str, TranscriptEntry] = {}

    def addEntry(self, section, grade: str):
        entry = TranscriptEntry(section, grade)
        course = section.getCourse()
        if course:
            courseNo = course.getCourseNo()
            self.__entries[courseNo] = entry

    def getGrade(self, courseNo):
        te = self.__entries.get(courseNo)
        if te is None:
            return None
        return te.getGrade()

    def getEntries(self):
        return self.__entries.copy()


# ================ STREAMLIT APPLICATION =================
def initialize_system():
    if 'courses' not in st.session_state:
        st.session_state.courses = {}
        st.session_state.sections = {}
        st.session_state.students = {}
        st.session_state.professors = {}

        # Create sample courses
        fp = Course("CS101", "Functional Programming", 4)
        oop = Course("CS201", "Object-Oriented Programming", 4)
        oop.addPrerequisites(fp)

        # Create sections
        fp_section = fp.scheduleOfSection("CS101-A", "Monday", "9:00 AM", "Room 101", 30)
        oop_section1 = oop.scheduleOfSection("CS201-A", "Tuesday", "10:00 AM", "Room 102", 25)
        oop_section2 = oop.scheduleOfSection("CS201-B", "Wednesday", "2:00 PM", "Room 103", 25)

        # Create professor
        prof = Professor("Dr. Smith", "P001", "Professor", "Computer Science")
        prof.agreeToTeach(fp_section)
        prof.agreeToTeach(oop_section1)
        prof.agreeToTeach(oop_section2)

        # store in section state
        st.session_state.courses = {
            "CS101": fp,
            "CS201": oop
        }

        st.session_state.sections = {
            "CS101-A": fp_section,
            "CS201-A": oop_section1,
            "CS201-B": oop_section2
        }
        st.session_state.professors = {"P001": prof}


# cac ham chuc nang
def main():
    st.set_page_config(
        page_title="Student Registration System",
        page_icon="🎓",
        layout="wide",
    )

    initialize_system()

    st.title("Student Registration System")
    st.markdown("---")

    # sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Student Management", "Course Management", "Enrollment", "Reports"]
    )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Student Management":
        show_student_management()
    elif page == "Course Management":
        show_course_management()
    elif page == "Enrollment":
        show_enrollment()
    elif page == "Reports":
        show_reports()


def show_dashboard():
    st.header("System Dashboard")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Courses", len(st.session_state.courses))

    with col2:
        st.metric("Total Sections", len(st.session_state.sections))

    with col3:
        st.metric("Total Students", len(st.session_state.students))

    with col4:
        st.metric("Total Professors", len(st.session_state.professors))

    st.subheader("📚 Available Courses")
    if st.session_state.courses:
        course_data = []
        for course in st.session_state.courses.values():
            course_data.append({
                "Course Code": course.getCourseNo(),
                "Course Name": course.getCourseName(),
                "Credits": course.getCredits(),
                "Sections": len(course.getSections()),
                "Prerequisites": len(course.getPrerequisites())
            })

        df = pd.DataFrame(course_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No courses available.")


def show_student_management():
    st.header("Student Management")
    tab1, tab2, tab3 = st.tabs(["Add Student", "View Students", "Delete Student"])

    with tab1:
        st.subheader("Add New Student")
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Student Name*")
                ssn = st.text_input("Student ID*")

            with col2:
                major = st.text_input("Major*")
                degree = st.selectbox("Degree", ["BSc", "MSc", "PhD"])

            submit = st.form_submit_button("Add Student")

            if submit:
                if name and ssn and major:
                    try:
                        if ssn not in st.session_state.students:
                            student = Student(name, ssn, major, degree)
                            st.session_state.students[ssn] = student
                            st.success(f"Student {name} added successfully!")
                        else:
                            st.error(f"Student ID {ssn} already exists!")

                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please fill in all required fields!")

    with tab2:
        st.subheader("Current Students")
        if st.session_state.students:
            student_data = []
            for student in st.session_state.students.values():
                student_data.append({
                    "Name": student.name,
                    "Student ID": student.ssn,
                    "Major": student.getMajor(),
                    "Degree": student.getDegree(),
                    "Enrolled Sections": len(student.getSections())
                })
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No students registered yet.")

    with tab3:
        st.subheader("Delete Student")

        if st.session_state.students:
            st.warning("⚠️ Warning: Deleting a student will remove them from all enrolled sections!")

            # Select student to delete
            student_to_delete = st.selectbox(
                "Select Student to Delete",
                options=list(st.session_state.students.keys()),
                format_func=lambda
                    x: f"{st.session_state.students[x].name} ({x}) - {st.session_state.students[x].getMajor()}",
                key="delete_student_select"
            )

            if student_to_delete:
                student = st.session_state.students[student_to_delete]
                enrolled_sections = student.getSections()

                # Show student details
                st.write(f"Student: {student.name}")
                st.write(f"Student ID: {student.ssn}")
                st.write(f"Major: {student.getMajor()}")
                st.write(f"Degree: {student.getDegree()}")
                st.write(f"Enrolled Sections: {len(enrolled_sections)}")

                # Show enrolled sections
                if enrolled_sections:
                    st.write("**Currently Enrolled In:**")
                    for section in enrolled_sections:
                        course = section.getCourse()
                        st.write(f"- {section.getSectionNo()} - {course.getCourseName() if course else 'Unknown'}")

                # Confirmation checkbox
                confirm_delete = st.checkbox(
                    f"I understand the consequences and want to delete student {student.name}",
                    key="confirm_delete_student"
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete Student", type="primary", disabled=not confirm_delete):
                        try:
                            # Remove student from all enrolled sections
                            for section in enrolled_sections:
                                section_students = section.getStudents()
                                if student in section_students:
                                    section._Section__students.remove(student)

                            # Remove student from session state
                            del st.session_state.students[student_to_delete]

                            st.success(f"Student {student.name} has been deleted successfully!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error deleting student: {e}")

                with col2:
                    if st.button("Cancel", key="cancel_delete_student"):
                        st.info("Delete operation cancelled.")
        else:
            st.info("No students available to delete.")


def show_course_management():
    st.header("Course Management")

    tab1, tab2, tab3, tab4 = st.tabs(["Add Course", "View Courses & Sections", "Delete Course", "Delete Section"])

    with tab1:
        st.subheader("Add New Course")

        with st.form("add_course_form"):
            col1, col2 = st.columns(2)

            with col1:
                courseNo = st.text_input("Course Code*")
                courseName = st.text_input("Course Name*")
                credits = st.number_input("Credits", min_value=1, max_value=6, value=3)

            with col2:
                prerequisites = st.multiselect(
                    "Prerequisites",
                    options=list(st.session_state.courses.keys()),
                    format_func=lambda x: f"{x} - {st.session_state.courses[x].getCourseName()}"
                )

            submit = st.form_submit_button("Add Course")

            if submit:
                if courseNo and courseName:
                    try:
                        if courseNo not in st.session_state.courses:
                            course = Course(courseNo, courseName, credits)

                            # Add prerequisites
                            for prereq_code in prerequisites:
                                prereq_course = st.session_state.courses[prereq_code]
                                course.addPrerequisites(prereq_course)

                            st.session_state.courses[courseNo] = course
                            st.success(f"Course {courseName} added successfully!")
                        else:
                            st.error("Course code already exists!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please fill in all required fields!")

        st.subheader("Add Section to Course")

        if st.session_state.courses:
            with st.form("add_section_form"):
                col1, col2 = st.columns(2)

                with col1:
                    selected_course = st.selectbox(
                        "Select Course",
                        options=list(st.session_state.courses.keys()),
                        format_func=lambda x: f"{x} - {st.session_state.courses[x].getCourseName()}"
                    )
                    sectionNo = st.text_input("Section Number*")
                    capacity = st.number_input("Seating Capacity", min_value=1, max_value=100, value=30)

                with col2:
                    day = st.selectbox("Day of Week",
                                       ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                    time = st.selectbox("Time",
                                        ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM",
                                         "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"])
                    room = st.text_input("Room*")

                submit_section = st.form_submit_button("Add Section")

                if submit_section:
                    if sectionNo and room and selected_course:
                        try:
                            if sectionNo not in st.session_state.sections:
                                course = st.session_state.courses[selected_course]
                                section = course.scheduleOfSection(sectionNo, day, time, room, capacity)
                                st.session_state.sections[sectionNo] = section
                                st.success(f"Section {sectionNo} added successfully!")
                            else:
                                st.error("Section number already exists!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Please fill in all required fields!")

    with tab2:
        st.subheader("Course and Section Details")

        if st.session_state.sections:
            section_data = []
            for section in st.session_state.sections.values():
                course = section.getCourse()
                professor = section.getProfessor()

                section_data.append({
                    "Section": section.getSectionNo(),
                    "Course": f"{course.getCourseNo()} - {course.getCourseName()}" if course else "Unknown",
                    "Day": section.getDayOfWeek(),
                    "Time": section.getTimeOfDay(),
                    "Room": section.getRoom(),
                    "Capacity": section.getCapacity(),
                    "Enrolled": section.getEnrolledCount(),
                    "Available": section.getCapacity() - section.getEnrolledCount(),
                    "Professor": professor.name if professor else "Not Assigned"
                })

            df = pd.DataFrame(section_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No sections available yet.")

    with tab3:
        st.subheader("Delete Course")

        if st.session_state.courses:
            st.warning(
                "⚠️ Warning: Deleting a course will also remove all its sections and may affect student enrollments!")

            # Select course to delete
            course_to_delete = st.selectbox(
                "Select Course to Delete",
                options=list(st.session_state.courses.keys()),
                format_func=lambda x: f"{x} - {st.session_state.courses[x].getCourseName()}",
                key="delete_course_select"
            )

            if course_to_delete:
                course = st.session_state.courses[course_to_delete]
                sections = course.getSections()

                # Show course details
                st.write(f"**Course:** {course.getCourseNo()} - {course.getCourseName()}")
                st.write(f"**Credits:** {course.getCredits()}")
                st.write(f"**Sections:** {len(sections)}")

                # Check if course is a prerequisite for other courses
                dependent_courses = []
                for other_course_code, other_course in st.session_state.courses.items():
                    if other_course_code != course_to_delete:
                        prerequisites = other_course.getPrerequisites()
                        if course in prerequisites:
                            dependent_courses.append(other_course_code)

                if dependent_courses:
                    st.error(f"⚠️ Cannot delete this course! It is a prerequisite for: {', '.join(dependent_courses)}")
                    st.info("Please remove this course as a prerequisite from other courses first.")
                    can_delete = False
                else:
                    can_delete = True

                    # Show affected students if any
                    affected_students = []
                    for section in sections:
                        students = section.getStudents()
                        for student in students:
                            if student.ssn not in [s.ssn for s in affected_students]:
                                affected_students.append(student)

                    if affected_students:
                        st.warning(f"This will affect {len(affected_students)} enrolled students:")
                        for student in affected_students:
                            st.write(f"- {student.name} ({student.ssn})")

                # Confirmation checkbox
                if can_delete:
                    confirm_delete = st.checkbox(
                        f"I understand the consequences and want to delete {course_to_delete}",
                        key="confirm_delete_course"
                    )

                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("🗑️ Delete Course", type="primary", disabled=not confirm_delete):
                            try:
                                # Remove students from sections and update their records
                                for section in sections:
                                    students_to_remove = section.getStudents().copy()
                                    for student in students_to_remove:
                                        student.dropSection(section)

                                # Remove sections from session state
                                sections_to_remove = [s.getSectionNo() for s in sections]
                                for section_no in sections_to_remove:
                                    if section_no in st.session_state.sections:
                                        del st.session_state.sections[section_no]

                                # Remove course from session state
                                del st.session_state.courses[course_to_delete]

                                st.success(
                                    f"Course {course_to_delete} and all its sections have been deleted successfully!")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error deleting course: {e}")

                    with col2:
                        if st.button("Cancel", key="cancel_delete_course"):
                            st.info("Delete operation cancelled.")
        else:
            st.info("No courses available to delete.")

    with tab4:
        st.subheader("Delete Section")

        if st.session_state.sections:
            st.warning("⚠️ Warning: Deleting a section will remove all enrolled students from it!")

            # Select section to delete
            section_to_delete = st.selectbox(
                "Select Section to Delete",
                options=list(st.session_state.sections.keys()),
                format_func=lambda
                    x: f"{x} - {st.session_state.sections[x].getCourse().getCourseName() if st.session_state.sections[x].getCourse() else 'Unknown'}",
                key="delete_section_select"
            )

            if section_to_delete:
                section = st.session_state.sections[section_to_delete]
                course = section.getCourse()
                students = section.getStudents()

                # Show section details
                st.write(f"**Section:** {section.getSectionNo()}")
                st.write(f"**Course:** {course.getCourseName() if course else 'Unknown'}")
                st.write(f"**Schedule:** {section.getDayOfWeek()} {section.getTimeOfDay()}")
                st.write(f"**Room:** {section.getRoom()}")
                st.write(f"**Enrolled Students:** {len(students)}")

                # Show enrolled students
                if students:
                    st.write("**Students to be removed:**")
                    for student in students:
                        st.write(f"- {student.name} ({student.ssn})")

                # Confirmation checkbox
                confirm_delete = st.checkbox(
                    f"I understand the consequences and want to delete section {section.getSectionNo()}",
                    key="confirm_delete_section"
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete Section", type="primary", disabled=not confirm_delete):
                        try:
                            # Remove students from section
                            students_to_remove = students.copy()
                            for student in students_to_remove:
                                student.dropSection(section)

                            # Remove section from course
                            if course:
                                course._Course__sections.remove(section)

                            # Remove section from session state
                            del st.session_state.sections[section_to_delete]

                            st.success(f"Section {section.getSectionNo()} has been deleted successfully!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error deleting section: {e}")

                with col2:
                    if st.button("Cancel", key="cancel_delete_section"):
                        st.info("Delete operation cancelled.")
        else:
            st.info("No sections available to delete.")


def show_enrollment():
    st.header("Student Enrollment")

    if not st.session_state.students:
        st.warning("No students available. Please add students first.")
        return

    if not st.session_state.sections:
        st.warning("No sections available. Please add sections first.")
        return

    tab1, tab2, tab3 = st.tabs(["Enroll Student", "Post Grades", "Drop Section"])

    with tab1:
        st.subheader("Enroll Student in Section")

        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox(
                "Select Student",
                options=list(st.session_state.students.keys()),
                format_func=lambda x: f"{st.session_state.students[x].name} ({x})"
            )

        with col2:
            available_sections = []
            for section_no, section in st.session_state.sections.items():
                if section.confirmSeatAvailability():
                    course = section.getCourse()
                    available_sections.append(section_no)

            if available_sections:
                selected_section = st.selectbox(
                    "Select Section",
                    options=available_sections,
                    format_func=lambda x: f"{x} - {st.session_state.sections[x].getCourse().getCourseName()}"
                )
            else:
                st.error("No sections with available seats!")
                selected_section = None

        if st.button("Enroll Student", disabled=not selected_section):
            student = st.session_state.students[selected_student]
            section = st.session_state.sections[selected_section]

            success, message = section.enroll(student)

            if success:
                st.success(message)
            else:
                st.error(message)

    with tab2:
        st.subheader("Post Grades")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_student_grade = st.selectbox(
                "Select Student",
                options=list(st.session_state.students.keys()),
                format_func=lambda x: f"{st.session_state.students[x].name} ({x})",
                key="grade_student"
            )

        with col2:
            student = st.session_state.students[selected_student_grade]
            enrolled_sections = [s.getSectionNo() for s in student.getSections()]

            if enrolled_sections:
                selected_section_grade = st.selectbox(
                    "Select Section",
                    options=enrolled_sections,
                    format_func=lambda x: f"{x} - {st.session_state.sections[x].getCourse().getCourseName()}",
                    key="grade_section"
                )
            else:
                st.info("Student is not enrolled in any sections.")
                selected_section_grade = None

        with col3:
            grade = st.number_input("Grade", min_value=0.0, max_value=10.0, step=0.1, value=5.0)

        if st.button("Post Grade", disabled=not selected_section_grade):
            section = st.session_state.sections[selected_section_grade]
            section.postGrade(student, str(grade))
            st.success(f"Grade {grade} posted for {student.name}!")

    with tab3:
        st.subheader("Drop Section")

        if st.session_state.students:
            col1, col2 = st.columns(2)

            with col1:
                selected_student_drop = st.selectbox(
                    "Select Student",
                    options=list(st.session_state.students.keys()),
                    format_func=lambda x: f"{st.session_state.students[x].name} ({x})",
                    key="drop_student"
                )

            with col2:
                student = st.session_state.students[selected_student_drop]
                enrolled_sections = student.getSections()

                if enrolled_sections:
                    section_options = [s.getSectionNo() for s in enrolled_sections]
                    selected_section_drop = st.selectbox(
                        "Select Section to Drop",
                        options=section_options,
                        format_func=lambda x: f"{x} - {st.session_state.sections[x].getCourse().getCourseName()}",
                        key="drop_section"
                    )
                else:
                    st.info("Student is not enrolled in any sections.")
                    selected_section_drop = None

            if st.button("Drop Section", disabled=not selected_section_drop):
                section = st.session_state.sections[selected_section_drop]

                # Remove student from section
                section._Section__students.remove(student)
                # Remove section from student
                student.dropSection(section)

                st.success(f"{student.name} has been dropped from {section.getSectionNo()}!")
        else:
            st.info("No students available.")


def show_reports():
    st.header("Reports & Analytics")

    tab1, tab2, tab3 = st.tabs(["Student Transcripts", "Section Enrollment", "Course Statistics"])

    with tab1:
        st.subheader("Student Transcripts")

        if st.session_state.students:
            selected_student = st.selectbox(
                "Select Student",
                options=list(st.session_state.students.keys()),
                format_func=lambda x: f"{st.session_state.students[x].name} ({x})",
                key="transcript_student"
            )

            student = st.session_state.students[selected_student]

            st.write(f"**Student:** {student.name}")
            st.write(f"**Student ID:** {student.ssn}")
            st.write(f"**Major:** {student.getMajor()}")
            st.write(f"**Degree:** {student.getDegree()}")

            st.subheader("Academic Record")

            transcript = student.getTranscript()
            entries = transcript.getEntries()

            if entries:
                transcript_data = []
                for course_no, entry in entries.items():
                    section = entry.getSection()
                    course = section.getCourse()

                    transcript_data.append({
                        "Course Code": course_no,
                        "Course Name": course.getCourseName() if course else "Unknown",
                        "Section": section.getSectionNo(),
                        "Credits": course.getCredits() if course else 0,
                        "Grade": entry.getGrade()
                    })

                df = pd.DataFrame(transcript_data)
                st.dataframe(df, use_container_width=True)

                # Calculate GPA
                total_points = sum(float(row["Grade"]) * row["Credits"] for _, row in df.iterrows())
                total_credits = sum(row["Credits"] for _, row in df.iterrows())
                gpa = total_points / total_credits if total_credits > 0 else 0

                st.metric("GPA", f"{gpa:.2f}")
            else:
                st.info("No grades recorded yet.")
        else:
            st.info("No students available.")

    with tab2:
        st.subheader("Section Enrollment Details")

        if st.session_state.sections:
            for section_no, section in st.session_state.sections.items():
                with st.expander(f"Section {section_no}"):
                    course = section.getCourse()
                    professor = section.getProfessor()

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Course:** {course}")
                        st.write(f"**Schedule:** {section.getDayOfWeek()} {section.getTimeOfDay()}")
                        st.write(f"**Room:** {section.getRoom()}")

                    with col2:
                        st.write(f"**Professor:** {professor.name if professor else 'Not Assigned'}")
                        st.write(f"**Capacity:** {section.getCapacity()}")
                        st.write(f"**Enrolled:** {section.getEnrolledCount()}")

                    students = section.getStudents()
                    if students:
                        st.write("**Enrolled Students:**")
                        for student in students:
                            st.write(f"- {student.name} ({student.ssn})")
                    else:
                        st.write("No students enrolled yet.")
        else:
            st.info("No sections available.")

    with tab3:
        st.subheader("Course Statistics")

        if st.session_state.courses:
            stats_data = []
            for course in st.session_state.courses.values():
                sections = course.getSections()
                total_capacity = sum(s.getCapacity() for s in sections)
                total_enrolled = sum(s.getEnrolledCount() for s in sections)

                stats_data.append({
                    "Course": f"{course.getCourseNo()} - {course.getCourseName()}",
                    "Sections": len(sections),
                    "Total Capacity": total_capacity,
                    "Total Enrolled": total_enrolled,
                    "Utilization %": f"{(total_enrolled / total_capacity * 100):.1f}%" if total_capacity > 0 else "0%",
                    "Prerequisites": len(course.getPrerequisites())
                })

            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)

            # Visualization
            if len(stats_data) > 0:
                st.subheader("Enrollment Visualization")

                chart_data = pd.DataFrame({
                    'Course': [row['Course'] for row in stats_data],
                    'Enrolled': [int(row['Total Enrolled']) for row in stats_data],
                    'Capacity': [int(row['Total Capacity']) for row in stats_data]
                })

                st.bar_chart(chart_data.set_index('Course'))
        else:
            st.info("No courses available.")


if __name__ == "__main__":
    main()