import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from tortoises.scholar.wos import AppWebKnowledge
import time
from time import sleep
from tortoises.util.help import time as t

from logger_initial import logger_init


class AppWebKnowledge2(AppWebKnowledge):
    logger = logger_init()

    def go_to_page(self, page=1):
        try:
            # enter page number
            selector = self.driver.find_element_by_class_name('goToPageNumber-input')
            # clear input
            selector.clear()
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            selector.send_keys(page)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            # submit page number
            selector.submit()
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "goToPageNumber-input")))
            if self.mode == 'slow':
                sleep(random.uniform(4, 6))
            self.num_items_current_page = self._items_current_page_count()
            self.current_page = page
            print(f'[{t()}]:\033[1;36m success\033[0m to fetch page '
                  f'<\033[1;34m { page }\033[0m / \033[1;34m{ self.num_pages }\033[0m > .')
        except Exception as e:
            self.logger.error(f'[{t()}]:fail to fetch page < 'f'{page} / { self.num_pages } > and skip .\n{e}')
            print(f'[{t()}]:\033[1;31m fail\033[0m to fetch page <\033[1;34m '
                  f'{page}\033[0m / \033[1;34m{ self.num_pages }\033[0m > and skip .\n{e}')

    def search(self, argument, mode='title'):

        print(
            f'[{t()}]:\033[1;36m searching\033[0m < \033[1;33m{argument}\033[0m > by < \033[1;35m{mode}\033[0m > .')

        """
        # step 0. clear history search records
        try:
            self.driver.find_element_by_id(
                'clearIcon1').click()
            if self.verbose:
                print(f'[{t()}]:\033[1;36m success\033[0m to clear history search records .')
            sleep(random.uniform(1, 3))
        except (NoSuchElementException, ElementNotInteractableException,
                ElementClickInterceptedException, ):
            pass
        """

        # step 1. enter searched argument
        try:
            selector = self.driver.find_element_by_xpath(
                "//div[@class='search-criteria-input-wr']/input"
            )
            selector.clear()
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            selector.send_keys(argument)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{t()}]:\033[1;36m success\033[0m to enter article title .')
            if self.mode == 'slow':
                sleep(random.uniform(1, 3))
        except NoSuchElementException:
            print(f'[{t()}]:\033[1;31m fail\033[0m to enter article title .')
            return

        # step 2. switch search mode
        try:
            self.switch_search_mode(mode)
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException,):
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            # minimize questionnaire column if exits
            self.hide_advertise_widget()
            try:
                self.switch_search_mode(mode)
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f'[{t()}]:\033[1;31m fail\033[0m to switch search mode, may have triggered exceptions .')
                return

        if self.mode == 'slow':
            sleep(random.uniform(1, 3))

        # step 3. click search button
        try:
            self.click_search_button()
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            # minimize questionnaire column if exits
            self.hide_advertise_widget()
            try:
                self.click_search_button()
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f'[{t()}]:\033[1;31m fail\033[0m to search articles, may have triggered exceptions .')
                return

        if self.verbose:
            print(f'[{t()}]:\033[1;37m searched ...\033[0m')
        if self.mode == 'slow':
            sleep(random.uniform(1, 3))

        # step 4. parse search results
        searched_titles = [item.text.strip() for item in self.driver.find_elements_by_xpath(
            "//div[@class='search-results-content']//a[@class='smallV110 snowplow-full-record']"
        )]

        if len(searched_titles) == 0:
            self.search_status = False
            self.unique_matched = False
            if self.verbose:
                print(f'[{t()}]:\033[1;31m fail\033[0m to parse the searched page .')
                print(f'[{t()}]:\033[1;31m none\033[0m matched result found .')
        elif len(searched_titles) == 1:
            self.search_status = True
            self.unique_matched = True
            self.searched_title = searched_titles[0]
            if self.verbose:
                print(f'[{t()}]:\033[1;36m success\033[0m to parse the searched page .')
                print(f'[{t()}]:\033[1;36m unique\033[0m matched result found .')
        else:
            self.search_status = True
            self.unique_matched = False
            if self.verbose:
                print(f'[{t()}]:\033[1;36m success\033[0m to parse the searched page .')
                print(f'[{t()}]:\033[1;33m multiple\033[0m matched results found .')
        if self.mode == 'slow':
            sleep(random.uniform(2, 3))
        return len(searched_titles)
    
    def fetch_home(self):

        # init status
        self.init()

        # step 1. login homepage
        try:
            if self.verbose:
                print(f'[{t()}]:\033[1;36m connecting to\033[0m < http://apps.webofknowledge.com > ...')
            self.driver.get('http://apps.webofknowledge.com')
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div")))
        except Exception as e:
            if self.verbose:
                print(f'[{t()}]:\033[1;31m fail\033[0m to login < http://apps.webofknowledge.com > .\n{e}')
            return 'fail'

        print(f'[{t()}]:\033[1;36m success\033[0m to login < http://apps.webofknowledge.com > .')
        if self.mode == 'slow':
            sleep(random.uniform(1, 3))

        # step 2. switch web language to english if not
        try:
            self.driver.find_element_by_xpath('//a[@title="English"]')
        except NoSuchElementException:
            for language in ['简体中文', '繁體中文', '日本語', '한국어', 'Português', 'Español', 'Русский']:
                try:
                    self.driver.find_element_by_xpath(f'//a[@title="{language}"]').click()
                    sleep(random.uniform(4, 6))
                    self.driver.find_element_by_xpath('//ul//a[contains(text(), "English")]').click()
                    WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, "search-criteria-input-wr")))
                    if self.verbose:
                        print(f'[{t()}]:\033[1;36m success\033[0m to switch web language from {language} to English.')
                    if self.mode == 'slow':
                        sleep(random.uniform(2, 4))
                    break
                except (NoSuchElementException, TimeoutException, ):
                    pass

