import requests
from bs4 import BeautifulSoup
from getpass import getpass

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

def LoginSuccess(S,content):
    Login_Response_Soup = BeautifulSoup(content,'html.parser')
    alert = Login_Response_Soup.select_one('div.alert')
    if (alert == None):
        return True
    else:
        return False

def getPage(S):    
    link = "https://cms.bahria.edu.pk/Logins/Student/"
    headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    # Initial Page Get Request
    response = S.get(link,headers=headers)
    content = response.content.decode()
    soup = BeautifulSoup(content,'html.parser')
    
    #Forming Dictionary for Data Payload 
    ContinueToPost = False

    event_validation = soup.select_one("#__EVENTVALIDATION")['value']
    view_state_generator = soup.select_one('#__VIEWSTATEGENERATOR')['value']
    view_state = soup.select_one('#__VIEWSTATE')['value']

    student_enrollment = input('Enter Enrollment(include hyphens(-)) : ')
    input_format = student_enrollment.count('-')
    if(input_format == 2):
        ContinueToPost = True
    if (ContinueToPost):    
        student_password = getpass('Enter Password : ')
        form_data = {
            '__LASTFOCUS' : "",
            '__EVENTTARGET' : "ctl00$BodyPH$btnLogin",
            '__EVENTARGUMENT' : "",
            '__VIEWSTATE' : view_state,
            '__VIEWSTATEGENERATOR' : view_state_generator,
            '__EVENTVALIDATION' : event_validation,
            'ctl00$BodyPH$tbEnrollment' : student_enrollment,
            'ctl00$BodyPH$tbPassword' : student_password,
            'ctl00$BodyPH$ddlInstituteID' : "2",
            'ctl00$BodyPH$ddlSubUserType' : "None",
            'ctl00$hfJsEnabled' :"0",
        }

        # Sending a Post Request for Login
        PostLink = "https://cms.bahria.edu.pk/Logins/Student/Login.aspx"
        try:
            print("Posting Link")
            Login_Response = S.post(PostLink,headers = headers, data=form_data)
            # Checking if Login Was Successful
            if(Login_Response.status_code == 200):

                if(LoginSuccess(S,Login_Response.content.decode())):
                    CourseLinks = getRegisteredCourses(S,headers)
                    GetAttendance(S,headers,CourseLinks)
                    return True
                else:
                    print('Login Unsuccessful, Please Try Again\n')
                    return False
        except Exception as e:
            print ("We ran into a Problem :( ")
            print (e)
    return False
def main():
    
    Startup_Text = '''
 ____        _          _          _____ __  __  _____ 
|  _ \      | |        (_)        / ____|  \/  |/ ____|
| |_) | __ _| |__  _ __ _  __ _  | |    | \  / | (___  
|  _ < / _` | '_ \| '__| |/ _` | | |    | |\/| |\___ \ 
| |_) | (_| | | | | |  | | (_| | | |____| |  | |____) |
|____/ \__,_|_| |_|_|  |_|\__,_|  \_____|_|  |_|_____/ 
                                                       
                                                       
         _   _                 _                      
    /\  | | | |               | |                     
   /  \ | |_| |_ ___ _ __   __| | __ _ _ __   ___ ___ 
  / /\ \| __| __/ _ \ '_ \ / _` |/ _` | '_ \ / __/ _ \\
 / ____ \ |_| ||  __/ | | | (_| | (_| | | | | (_|  __/
/_/    \_\__|\__\___|_| |_|\__,_|\__,_|_| |_|\___\___|
                                                      
                                                      
  _____                                      
 / ____|                                     
| (___   ___ _ __ __ _ _ __  _ __   ___ _ __ 
 \___ \ / __| '__/ _` | '_ \| '_ \ / _ \ '__|
 ____) | (__| | | (_| | |_) | |_) |  __/ |   
|_____/ \___|_|  \__,_| .__/| .__/ \___|_|   
                      | |   | |              
                      |_|   |_|           
    '''
    print(Startup_Text)
    # Creating Session
    while(True):
        with requests.session() as S:
            if(getPage(S) == True):
                break

if __name__ == "__main__":
    main()