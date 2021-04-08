import os
import json
import uuid
import time
import requests
import unittest
from appium import webdriver
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.touch_action import TouchAction


CURRENT_DIR = os.path.dirname(__file__)
LOGIN_EMAIL = 'testuser@test.com'
LOGIN_PASSWORD = 'Test12345'
PROJECT_NAME = 'TestProject'


class ToDoIstAPI:
    
    def __init__(self):
        
        self.project_id = None
        self.api_token = 'ed64ece19ecfdfa9ebc94f9bf2fd8571e016d905'
        self.api_url = 'https://api.todoist.com/rest/v1/'
       
    def create_new_project(self, name) -> int:
        """
        Description: Create a new project using API.
        """
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['X-Request-Id'] = str(uuid.uuid4())
        headers['Authorization'] = 'Bearer %s' % self.api_token
        data = data=json.dumps({"name": name})
        url = self.api_url + 'projects'
        response = requests.post(url, data=data, headers=headers)
        assert response.status_code == 200
        return response.json()['id']
        
    def delete_project(self, project_id):
        """
        Description: Delete the project
        """
        headers = {"Authorization": "Bearer %s" % self.api_token}
        url = self.api_url + 'projects/' + str(project_id)
        requests.delete(url, headers=headers)
    
    def get_tasks(self, project_id) -> list:
        """
        Description: Get the all task 
        """
        headers = {"Authorization": "Bearer %s" % self.api_token}
        url = self.api_url + 'tasks'
        response = requests.get(url, headers=headers, params={'project_id': project_id})
        return response.json()
    
    def reopen_task(self, task_id):
        """
        DEscription: Reopen the completes task
        """
        headers = {"Authorization": "Bearer %s" % self.api_token}
        url = self.api_url + 'tasks/{}/reopen'.format(task_id)
        response = requests.post(url, headers=headers)
        return response.status_code 
    
    def get_task_id_by_content(self, project_id: int, content: str):
        """
        Description: Get the task id by task content
        """
        tasks = self.get_tasks(project_id)
        for task in tasks:
            if task['content'] == content:
                return task['id']
            
class ToDoIstMobileApp:
    
        
    def invoke_app(self):
        
        desired_caps = {}
        desired_caps['deviceName'] = 'emulator-5554'
        desired_caps['platformName'] = 'Android'
        desired_caps['version'] = '10'  
        desired_caps['appPackage'] = 'com.todoist'
        desired_caps['appActivity'] = 'com.todoist.activity.HomeActivity'
        desired_caps['app'] = os.path.join(CURRENT_DIR, 'todoist_15.0.4-6030.apk')
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(30)
    
    def login(self) -> str:
        """
        1.Click on continue with email option
        2.Enter the email and password then click in login button
        3.Expand the side bar menu and read the user name
        """
        self.driver.find_element_by_id('com.todoist:id/btn_welcome_continue_with_email').click()
        self.driver.find_element_by_id('com.todoist:id/email_exists_input').send_keys(LOGIN_EMAIL)
        self.driver.find_element_by_id('com.todoist:id/btn_continue_with_email').click()
        self.driver.find_element_by_id('com.todoist:id/log_in_password').send_keys(LOGIN_PASSWORD)
        self.driver.find_element_by_id('com.todoist:id/btn_log_in').click()
        time.sleep(3)
        
    def get_projects(self) -> list:
        """
        Click on side bar menu and read the all projects name
        """
        self.select_navigation_menu("Projects")
        projects = []
        project_elements = self._get_sub_menu_elements('Projects')
        for project in project_elements:
            project_name = project.find_element_by_id('com.todoist:id/name').text.strip()
            projects.append(project_name)
        return projects
    
    def get_tasks(self) -> list:
        """
        Read the task from mobile app and retun
        """
        tasks_ele = self.driver.find_elements_by_id('com.todoist:id/text')
        tasks = [task.text.strip() for task in tasks_ele]
        return tasks
    
    def create_taks(self, name: str):
        """
        Create the new task in mobile app
        """
        self.driver.find_element_by_id('com.todoist:id/fab').click()
        self.driver.find_element_by_id('android:id/message').send_keys(name)
        self.driver.find_element_by_accessibility_id('Add').click()
        time.sleep(5)
        self.driver.back()
    
    def complete_task(self, name: str):
        """
        Click on task check mark to complete the task
        """
        tasks = self.get_tasks()
        if name in tasks:
            task_index = tasks.index(name)
            task_checkbox = self.driver.find_elements_by_id('com.todoist:id/checkmark')[task_index]
            task_checkbox.click()
        else:
            error_msg = "[{}] Task not exists".format(name)
            raise KeyError(error_msg)
        time.sleep(5)
        
    def select_navigation_menu(self, menu: str) -> None:
        """
        Select the navigation menu(Side bar menu)
        """
        xpath = "//android.widget.FrameLayout[@resource-id='com.todoist:id/navigation_fragment']//android.widget.TextView[@text='{}']"
        self.driver.find_element_by_xpath(xpath.format(menu)).click()
        time.sleep(1)
        
    def select_project(self, name: str) -> None:
        """
        Select the project
        """
        project_elements = self._get_sub_menu_elements('Projects')
        for project_ele in project_elements:
            project = project_ele.find_element_by_id('com.todoist:id/name')
            if project.text.strip() == name:
                project.click()
                break
        else:
            error_msg = "[{}] project not exists".format(name)
            raise KeyError(error_msg)
        time.sleep(1)
    

    def _get_sub_menu_elements(self, menu: str) -> list:
        """
        Get the sub menu elements of navigation menu
        """
        xpath = "//android.widget.FrameLayout[@resource-id='com.todoist:id/navigation_fragment']//android.widget.TextView[@text='{}']/parent::android.widget.RelativeLayout/following-sibling::*"
        elements = self.driver.find_elements_by_xpath(xpath.format(menu))
        sub_menu_elements = []
        for element in elements:
            resource_id = element.get_attribute('resourceId')
            if resource_id == 'android:id/content':
                sub_menu_elements.append(element)
            else:
                break
        return sub_menu_elements
            
    def open_navigation_menu(self):
        """
        Click on navigation menu icon to open navigation menu
        """
        self.driver.find_element_by_accessibility_id('Change the current view').click()
            
    def close_navigation_menu(self):
        """
        Close the navigation menu by press back button if navigation opened.
        """
        self.driver.implicitly_wait(1)
        navigation_menu = self.driver.find_elements_by_id('com.todoist:id/navigation_fragment')
        if navigation_menu:
            self.driver.back()
            time.sleep(1)
        self.driver.implicitly_wait(30)
        
    def refresh(self):
        """
        Refresh the content by swiping 
        """
        toolbar = self.driver.find_element_by_id('com.todoist:id/toolbar')
        start_x = (toolbar.size['width'] // 2) +  toolbar.location['x']
        start_y = toolbar.size['height'] + toolbar.location['y'] + 10
        end_x = start_x
        end_y = start_y * 3
        TouchAction(self.driver).long_press(x=start_x, y=start_y).move_to(x=end_x, y=end_y).release().perform()
        time.sleep(2)
        
class TestToDoIst(unittest.TestCase):
    
    project_id = None
    
    @classmethod
    def setUpClass(cls) -> None:
        
        AppiumService().start()
        cls.todoistapi = ToDoIstAPI()
        cls.todoistapp = ToDoIstMobileApp()
        cls.todoistapp.invoke_app()
        
    def test_create_project(self):
        
        """
        STEP 1: Create test project via API
        """
        TestToDoIst.project_id = self.todoistapi.create_new_project(PROJECT_NAME)
       
        """
        STEP 2: Login into mobile application.
        """
        self.todoistapp.login()
        
        """
        STEP 3: Verify on mobile that project is created
        """
        self.todoistapp.open_navigation_menu()
        actual_projects = self.todoistapp.get_projects()
        self.todoistapp.close_navigation_menu()
        self.assertIn(PROJECT_NAME, actual_projects, 'Verify on mobile that project is created')
        
    def test_create_task_via_mobile_phone(self):
        
        """
        STEP 1: Create test task via mobile application in test project.
        """
        task_name = "TestTask1"
        self.todoistapp.open_navigation_menu()
        self.todoistapp.select_project(PROJECT_NAME)
        self.todoistapp.create_taks(task_name)
        actual_tasks = self.todoistapp.get_tasks()
        self.assertIn(task_name, actual_tasks, 'Verify task created in mobile app')
        
        """
        STEP 2: API: Verify that task created correctly.
        """
        actaul_tasks = [task['content'] for task in self.todoistapi.get_tasks(self.project_id)]
        self.assertIn(task_name, actaul_tasks, 'Verify that task created correctly')
        
        
    def test_reopen_task(self):
        
        """
        STEP 1: Open mobile application
        STEP 2: Open test project
        """
        self.todoistapp.open_navigation_menu()
        self.todoistapp.select_project(PROJECT_NAME)
        
        """
        STEP 3: Created test task
        """
        task_name = "TestTask2"
        self.todoistapp.create_taks(task_name)
        actual_tasks = self.todoistapp.get_tasks()
        self.assertIn(task_name, actual_tasks, 'Verify task created in mobile app')
        task_id = self.todoistapi.get_task_id_by_content(self.project_id, task_name)
        
        """
        STEP 4: Complete test task.
        """
        self.todoistapp.complete_task(task_name)
        actual_tasks = self.todoistapp.get_tasks()
        self.assertNotIn(task_name, actual_tasks, 'Verify task completed')
    
        """
        STEP 5: Reopen test task via API.
        """
        status_code = self.todoistapi.reopen_task(task_id)
        assert status_code == 204
        time.sleep(2)
        
        """
        STEP 6: Mobile: Verify that test task appears in your test project.
        """
        self.todoistapp.refresh()
        actual_tasks = self.todoistapp.get_tasks()
        self.assertIn(task_name, actual_tasks, 'Verify that test task appears in your test project')
        
    @classmethod
    def tearDownClass(cls):
        
        cls.todoistapi.delete_project(cls.project_id)
        cls.todoistapp.driver.quit()
        AppiumService().start()
        
if __name__ == '__main__':
    unittest.main()