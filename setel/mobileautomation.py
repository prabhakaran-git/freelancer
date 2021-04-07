import requests
import unittest
import json
import uuid

class ToDoIst(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        
        cls.api_token = '00173b56471ee357af81793a95bebb5432594824'
        cls.email = 'prabha393@gmail.com'
        cls.api_url = 'https://api.todoist.com/rest/v1/'
        cls.password = 'Test12345'
        cls.project_name = 'TestProject'
        cls.project_id = None

    @classmethod
    def tearDownClass(cls) -> None:
        
        if cls.project_id:
            cls._delete_project()

    def test_create_project(self):
        """
        Description: Create the new project via API and verify whether project created.
        """
        headers={
        "Content-Type": "application/json",
        "X-Request-Id": str(uuid.uuid4()),
        "Authorization": "Bearer %s" % self.api_token
        }
        data = data=json.dumps({"name": self.project_name})
        url = self.api_url + 'projects'
        response = requests.post(url, data=data, headers=headers) 
        print(response)
        assert response.status_code == 200
        assert self.project_name in response.json()['name']
        self.project_id = response.json()['id']

    @classmethod
    def _delete_project(cls):
        """
        Description : Delete the project via API
        """
        headers = {"Authorization": "Bearer %s" % cls.api_token}
        url = cls.api_url + 'projects/' + str(cls.project_id)
        requests.delete(url, headers=headers)


if __name__ == '__main__':
    unittest.main()