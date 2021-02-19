import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from random import choice

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; Avant Browser; '
    'SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0'
]


def get_user_agent(random: bool) -> str:
    if random:
        return choice(USER_AGENTS)
    else:
        return USER_AGENTS[0]


def get_headers(random: bool) -> dict:
    return {'User-Agent': get_user_agent(random)}


def init_option(headless=True, limit=True, path=''):
    options = Options()
    options.add_argument(f'--user-agent={get_user_agent(random=True)}')
    if limit:
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        wos_path = os.path.join(os.getcwd(), 'WOS')
        if path != '':
            paper_path = os.path.join(wos_path, path)
        else:
            paper_path = wos_path
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': paper_path}
        options.add_experimental_option('prefs', prefs)
    if headless:
        options.add_argument('--headless')
    return options


def start_chrome(headless=True, limit=True, delete_cookies=True, maximize=True, enigma=False, path=''):
    chrome_options = init_option(headless=headless, limit=limit, path=path)
    if enigma:
        chrome_driver = EnigmaWebDriver(options=chrome_options)
    else:
        chrome_driver = webdriver.Chrome(options=chrome_options)
#         chrome_driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)
    if delete_cookies:
        chrome_driver.delete_all_cookies()
    if maximize:
        chrome_driver.maximize_window()
    return chrome_driver


def start_firefox():
    firefox_driver = webdriver.Firefox()
    return firefox_driver


def start_phantomjs():
    phantomjs_driver = webdriver.PhantomJS()
    return phantomjs_driver


class EnigmaWebDriver(WebDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def find_element_by_class_name(self, name):
        element = None
        try:
            element = super().find_element_by_class_name(name)
        except NoSuchElementException:
            pass
        return element

    def find_element_by_id(self, id_):
        element = None
        try:
            element = super().find_element_by_id(id_)
        except NoSuchElementException:
            pass
        return element

    def find_element_by_xpath(self, xpath):
        element = None
        try:
            element = super().find_element_by_xpath(xpath)
        except NoSuchElementException:
            pass
        return element


if __name__ == '__main__':
    driver = start_chrome(enigma=True)
    driver.get('http://www.baidu.com/')

    driver.find_element_by_class_name('nothing')
    driver.find_element_by_class_name('s_ipt')
