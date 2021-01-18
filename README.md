# H.O.R.S.
Hospitality - Online - Registration - System

HORS is an online registration system created to optimize the International Monterrey Model United Nations (IMMUNS)
event's assignment delivery to teachers from all over Mexico.

## How does it work?
IMMUNS staff populate the system with the committees and delegations of the newest iteration of IMMUNS.

Teachers then sign up with a key given by their IMMUNS representative. The system will automatically detect 
the number of students they teacher paid for and allow the teacher to select what type of delegations they want.

Teachers can then log student information like their name and grade. Staff can see real time from the admin
console what assignments have been filled, how many assignments are still available, and much more.

## Features
- Admin panel with:
    - View of all assignments
    - Search filters
    - Manual assigning
    - Add or remove committees and countries
    - Add or remove committee room numbers
    - Teacher or school information
- Password protected staff and teacher account with encryption
- Teacher portal with:
    - Assignment list
    - Name and grade field for each assignment
    - Settings page to change password, name, school, etc
- Sign up page for new teachers
- Randomized assignments to all teachers
- Teachers can decide what type of assignments they want
    - English / Spanish
    - Middle School / High School
    - Regular Assignments / Important Assignments
    - Regular Committees / Advanced Committees
    
## Project History
This project was created during my senior year (2017) for my AP CPSC P (CS50) class. The project was then presented 
to the IMMUNS executive team and they decided to use it for IMMUNS 2018 and onward.

Ever since, new IMMUNS staff have called me to ask for changes, improvements, bug fixes, etc. The project has 
gone over a lot of changes from its first use, but thanks to this, it has been a integral part of every event ever since.

## What does it solve?
Before HORS, IMMUNS staff had to manually assign "assignments" (countries within a committee) to over 15 different
teachers located all around mexico. They used a huge white board to know what assignments were available, they tried to 
be fair and random, and it took them hours of work to do this. On top of that, they suffered of many issues like 
assigning the same assignment to two schools, forgetting to assign important assignments, etc.

When HORS was introduced it solved all the problems listed above, and it removed all the work load form the staff so they 
could concentrate on creating an amazing event, while the web app handled the assignments. 

## Technologies  
This project uses:
- Python
- Flask
- SQLite
- Jinja / HTML / CSS / JS

## Installation
You need to install all requirements found on requirements.txt

## Deployment
Currently deployed on Digital Ocean but will probably transfer over to AWS.

