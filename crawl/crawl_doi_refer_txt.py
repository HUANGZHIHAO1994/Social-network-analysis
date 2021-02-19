import os
from tqdm import tqdm
from config import WOS_Articles
from logger_initial import logger_init
import time
from driver_init import start_chrome
from selenium.common.exceptions import WebDriverException
from wos_crawl_inherit import AppWebKnowledge2


def filerename(wos_path, num_id):
    filelist = os.listdir(wos_path)
    if "savedrecs.txt.crdownload" in filelist:
        time.sleep(1)
        filerename(wos_path, num_id)
    else:
        for file in filelist:
            if "savedrecs" in file:
                os.renames(os.path.join(wos_path, file),
                           os.path.join(wos_path, '{}.txt'.format(num_id)))


def crawl_func(results):
    for result in results:
        
        doi = result['_id']
        num_id = result['num_id']
        apk = AppWebKnowledge2(headless=True, verbose=True)
        wos_path = os.path.join(os.getcwd(), 'WOS_REFER')
        if not os.path.exists(wos_path):
            os.makedirs(wos_path)
        apk.driver = start_chrome(headless=True, path=wos_path)
        print(result['num_id'])
        result_fetch_home = apk.fetch_home()
        if result_fetch_home == 'fail':
            apk.driver.quit()
            time.sleep(50)
            crawl_func(results)

        # 还是不能直接用doi命名txt
        search_result = apk.search(argument=doi, mode='doi')
        if search_result == 0:
            search_result = apk.search(argument=result['title'], mode='title')
            if search_result == 0:
                article_update = dict()
                article_update['research_areas'] = ''
                article_update['category'] = ''
                article_update['lang'] = ''
                article_update['keywords'] = ''
                article_update['keywords_plus'] = ''
                article_update['vol'] = ''
                article_update['issue'] = ''
                article_update['cite_references_number'] = 0
                article_update['cited_number'] = 0
                article_update['author_address'] = ''
                article_update['publisher'] = ''
                article_update['crawl_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                WOS_Articles.update_one({'_id': doi},
                                        {'$set': article_update})
                continue


        apk.search_init()
        # apk.fetch_current_page(index=apk.num_items_current_page)
        apk.fetch_current_page(index=0)

        # 在原有基础上增加一些字段
        apk.expand_all_fields()
        info = apk.parse_article()
        # print(info)
        article_update = dict()
        article_update['research_areas'] = info.get('ra', '')
        article_update['category'] = info.get('category', '')
        article_update['lang'] = info.get('language', '')
        article_update['keywords'] = info.get('keywords', '')
        article_update['keywords_plus'] = info.get('keywords_plus', '')
        article_update['vol'] = info.get('vol', '')
        article_update['issue'] = info.get('issue', '')
        article_update['cite_references_number'] = int(info.get('cited', 0))
        article_update['cited_number'] = int(info.get('citing', 0))
        article_update['author_address'] = info.get('c1', '')
        article_update['publisher'] = info.get('publisher', '')
        article_update['crawl_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(article_update)

        WOS_Articles.update_one({'_id': doi},
                                {'$set': article_update})

        try:
            apk.driver.find_element_by_xpath(
                "//a[@title='View this record’s bibliography']").click()
            # 增加 txt 导出
            apk.driver.find_element_by_xpath('//button[@id="exportTypeName"]').click()
            time.sleep(0.5)
            apk.driver.find_element_by_xpath(
                '//a[@title="Export the selected records to a tab-delimited file, other reference software, and more"]').click()

            apk.driver.find_element_by_xpath('//input[@id="numberOfRecordsRange"]').click()
            # 一般不会大于500
            # apk.driver.find_element_by_xpath('//input[@id="markFrom"]').clear()
            # apk.driver.find_element_by_xpath('//input[@id="markFrom"]').send_keys(start_result)
            # apk.driver.find_element_by_xpath('//input[@id="markTo"]').clear()
            # apk.driver.find_element_by_xpath('//input[@id="markTo"]').send_keys(end_result)
            time.sleep(0.3)
            apk.driver.find_element_by_xpath('//span[@id="select2-bib_fields-container"]').click()
            apk.driver.find_element_by_xpath(
                '//li[contains(text(),"Author, Title, Source, Abstract")]').click()
            time.sleep(0.5)
            apk.driver.find_element_by_xpath('//span[@id="select2-saveOptions-container"]').click()
            time.sleep(0.2)
            apk.driver.find_element_by_xpath(
                '//li[contains(text(),"Plain Text")]').click()

            apk.driver.find_element_by_xpath('//button[@id="exportButton"]').click()
        except Exception as e:
            print(e)

        time.sleep(0.5)
        filerename(wos_path, num_id)
        apk.driver.quit()



if __name__ == '__main__':
    # logger = logger_init()
#     skip = 502
#    多服务器同时爬取
    limit = 1
    start = 179284
    end = 179350
    for skip in range(start, end):
        results = WOS_Articles.find({}, no_cursor_timeout=True).skip(skip).limit(limit)
        crawl_func(results)

    # # initialize
    # filename_to_doi = dict()
    # dois = ['10.1080/15567249.2020.1808913', '10.1108/JIABR-01-2020-0004']
    # for index, i in enumerate(dois):
    #     filename_to_doi.update({str(index): i})
    # with open("filename_to_doi.txt", "w") as f:
    #     f.write(str(filename_to_doi))
    # doi_to_filename = {value: key for key, value in filename_to_doi.items()}
