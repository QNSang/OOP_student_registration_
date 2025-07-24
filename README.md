# OOP_student_registration_streamlit
Lab exercise for MTH10407_OOP (Object-Oriented Programming) at HCMUS. Built with Python and Streamlit
---

### Student Management
- Add new student to the system.
- View the list of all existing students.

### Course Management
- Create courses with details such as course_number, name, and credits
- Set prerequisites for courses
- Schedule sections (Classes) with time, room, and seat capacity

### Section Enrrollment
- 
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

