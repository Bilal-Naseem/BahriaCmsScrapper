# BahriaCmsScrapper
Using BeautifulSoup the following code will scrape attendance of the current enrolled courses from Bahria CMS

Note:
> This script was only created for learning purposes
> and doesnot mean any harm to the CMS of Bahria University.

Libraries used in the following scripts are
```python
import requests
from bs4 import BeautifulSoup
```
Initially Main function was called which then created a session.
The Created Session will now be used to login and scrape data from CMS.

```python

def main():
    # Creating Session
    with requests.session() as S:
        getPage(S)

if __name__ == "__main__":
    main()
```

Once Session created a getPage function was called which was used to get the initial login form
and submit a post request with all of the necessary headers and data payload.

```python
def getPage(S):    
    link = "https://cms.bahria.edu.pk/Logins/Student/"
    headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    # Initial Page Get Request
    response = S.get(link,headers=headers)
    content = response.content.decode()
    soup = BeautifulSoup(content,'html.parser')
    
    #Forming Dictionary for Data Payload 
    event_validation = soup.select_one("#__EVENTVALIDATION")['value']
    view_state_generator = soup.select_one('#__VIEWSTATEGENERATOR')['value']
    view_state = soup.select_one('#__VIEWSTATE')['value']
    form_data = {
        '__LASTFOCUS' : "",
        '__EVENTTARGET' : "ctl00$BodyPH$btnLogin",
        '__EVENTARGUMENT' : "",
        '__VIEWSTATE' : view_state,
        '__VIEWSTATEGENERATOR' : view_state_generator,
        '__EVENTVALIDATION' : event_validation,
        'ctl00$BodyPH$tbEnrollment' : "InputEnrollment",
        'ctl00$BodyPH$tbPassword' : "InputPassword",
        'ctl00$BodyPH$ddlInstituteID' : "2",
        'ctl00$BodyPH$ddlSubUserType' : "None",
        'ctl00$hfJsEnabled' :"0",
    }

    # Sending a Post Request for Login
    PostLink = "https://cms.bahria.edu.pk/Logins/Student/Login.aspx"
    Login_Response = S.post(PostLink,headers = headers, data=form_data)

    # Checking if Login Was Successful
    if(Login_Response.status_code == 200):
        CourseLinks = getRegisteredCourses(S,headers)
        GetAttendance(S,headers,CourseLinks)
```

After the Login attempt was successful, it is time to scrape links for all the current registered courses,
which was done by function named **getRegisteredCourses()** and will return a list of the registered courses.

```python
def getRegisteredCourses(S,headers):
    # Redirecting to courses Page
    Newlink = "https://cms.bahria.edu.pk/Sys/Student/CourseRegistration/RegisteredCourses.aspx"

    # Initial Page Get Request
    Registered_Courses_Response = S.get(Newlink,headers=headers)
    Registered_Courses_Content = Registered_Courses_Response.content.decode()
    Registered_Courses_Soup = BeautifulSoup(Registered_Courses_Content,'html.parser')

    # Getting Links to Current Semester Courses
    CurrentSemesterContent = Registered_Courses_Soup.select("div.table-responsive table.table tbody")[0]
    All_Links = CurrentSemesterContent.select("td a")
    Extracted_Links = []
    for eachLink in All_Links:
        CourseLink = eachLink['href']
        Extracted_Links.append(CourseLink[2:])

    return Extracted_Links
```
once the list of courses was returned it was passed to a function named **GetAttendance()**,
which then will get the attendance summary of the courses provided in the list and print them on console.

```python
def GetAttendance(S,headers,Extracted_Links):
    NewBaseLink = "https://cms.bahria.edu.pk/Sys/Student"
    for eachCourse in Extracted_Links:
        CoursePageResponse = S.get(NewBaseLink+eachCourse,headers=headers)
        CoursePageContent = CoursePageResponse.content.decode()
        CoursePageSoup = BeautifulSoup(CoursePageContent,'html.parser')

        CourseTitle = CoursePageSoup.select_one("#BodyPH_lblCourseTitle").text
        TableFooter = []
        TableFooter = CoursePageSoup.select("tfoot tr td")
        if(len(TableFooter) != 0):
            Total_Hours = TableFooter[-3].text
            Present_Hours = TableFooter[-2].text
            Absent_Hours = TableFooter[-1].text

            print(f"{CourseTitle} : ")
            print(f"\tTotal Hours : {Total_Hours}")
            print(f"\tAbsent Hours :{Absent_Hours}")
            print(f"\tPresent Hours : {Present_Hours}")
        else:
            print(f"{CourseTitle} : ")
            print("\t No Record Found")
```

The Output of the Script which contains Attendance Summary is shown below
  ![Scrapped Attendance Summary](./CMS_Scrapper_Attendance.PNG)