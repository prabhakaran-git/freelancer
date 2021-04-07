from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
import pandas
import unittest

class Taks(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.search_keyword = 'Iphone 11'
        cls.data_list = []
        cls.driver = Chrome()
        cls.driver.maximize_window()
        cls.driver.implicitly_wait = 30
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        print(cls.data_list)
        
    def test_amazon(self):
        amazon_url = 'https://www.amazon.in'
        
        #Navigate to the amazon website
        self.driver.get(amazon_url)

        #Enter the seach keyword in search text box
        search_textbox = self.driver.find_element_by_id("twotabsearchtextbox")
        search_textbox.send_keys(self.search_keyword)
        search_textbox.send_keys(Keys.ENTER)

        #Validate the result
        actual_result = self.driver.find_element_by_css_selector("div.sg-col-14-of-20").text
        expected_result = 'results for "{}"'.format(self.search_keyword)
        assert expected_result in actual_result

        #Get the results and read the product name, price and link
        results = self.driver.find_elements_by_css_selector("div[data-component-type='s-search-result']")
        for result in results:
            name_ele = result.find_element_by_css_selector("h2.a-size-mini>a")
            name = name_ele.text.strip()
            link = amazon_url + name_ele.get_attribute('href')
            price_ele = result.find_elements_by_css_selector("span.a-price-whole")
            price = price_ele[0].text.strip() if price_ele else ''
            self.data_list.append(['Amazon', name, price, link])

    def test_ebay(self):
        ebay_url = 'https://www.ebay.com/'
        
        #Navigate to the ebay website
        self.driver.get(ebay_url)

        #Enter the seach keyword in search text box
        search_textbox = self.driver.find_element_by_id("gh-ac")
        search_textbox.send_keys(self.search_keyword)
        search_textbox.send_keys(Keys.ENTER)

        #Validate the result
        actual_result = self.driver.find_element_by_css_selector("h1.srp-controls__count-heading").text
        expected_result = 'results for {}'.format(self.search_keyword)
        assert expected_result in actual_result

    def generate_report(self):
        pass

if __name__ == '__main__':
    unittest.main()