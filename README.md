# OOP_student_registration_streamlit
Lab exercise for MTH10407_OOP (Object-Oriented Programming) at HCMUS. Built with Python and Streamlit
---
A simple web application built with Python and Streamlit to simulate a course registration system for students. This exercise focuses on applying OOP principles to build system.

<img width="2150" height="996" alt="image" src="https://github.com/user-attachments/assets/5947e32a-4c51-4650-8923-8527d37ac6ff" />


## Description
The system allows admin to perform basic operations of registrar's office
*  **Course Management:** Add/view courses, credits and prerequisites.
*  **Section Management:** Open course sections with specific schedules, rooms and capacities.
*  **Student Management:** Add/view student information.
*  **Enrollment:** Enroll students in course sections, automatically checking seat availability and prerequisites.
## Future Development
* **Presistent Data Storage**:
  Integrate with databases such as **SQlite** or **PostgreSQL** to store presistently instead of replying on 'st.session_state'.
* **User Role Management**:
  Implement an authentication system (login/logout) with different user roles: Admin, Student, Professor
  Each role should have access to different features and interfaces.
* **UI/UX Improvements**
* **Application Deployment**:
  Deploy the application to platforms such as:
  - [Streamlit Community Cloud](https://streamlit.io/cloud)
  - [Heroku](https://www.heroku.com/)
  - [AWS](https://aws.amazon.com/)
  - [Render](https://render.com/)

##
                                        MTH10407_Object-Oriented Programming
```mermaid
classDiagram
    class Person {
        -ssn: String
        -name: String
    }

    class Professor {
        -title: String
        -department: String
        +agreeToTeach()
    }

    class Student {
        -major: String
        -degree: String
        +addSection()
        +dropSection()
        +isEnrolledIn()
    }

    class Course {
        -courseNo: String
        -courseName: String
        -credits: int
        +scheduleSection()
        +addPrerequisite()
        +hasPrerequisites()
    }

    class Section {
        -sectionNo: String
        -dayOfWeek: String
        -timeOfDay: String
        -room: String
        -seatingCapacity: int
        +enroll()
        +drop()
        +postGrade()
        +confirmSeatAvailability()
    }

    class TranscriptEntry {
        -grade: float
    }

    class Transcript {
        +verifyCompletion()
    }

    class ScheduleOfClasses {
        -semester: String
    }

    %% Inheritance
    Professor --|> Person
    Student --|> Person

    %% Associations
    Professor "1" --> "*" Section : teaches
    Student "1" --> "*" Section : attends
    Student "1" --> "1" Transcript : maintains
    Transcript "1" o-- "*" TranscriptEntry
    Course "1" --> "*" Section : offered as
    Course "*" --> "*" Course : prerequisite
    Section "*" --> "*" TranscriptEntry
    ScheduleOfClasses "1" o-- "*" Section

