# import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
import datetime
import time
import csv
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import NoSuchElementException
from pynput.keyboard import Listener, Key
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# from selenium.common import exceptions
# from selenium.webdriver.chrome.options import *
# options = webdriver.ChromeOptions()
#
# prox = Proxy()
# prox.proxy_type = ProxyType.MANUAL
# # prox.autodetect = False
# prox.http_proxy = "127.0.0.1:9000"
# prox.socks_proxy = "127.0.0.1:9000"
# prox.ssl_proxy = "127.0.0.1:9000"
#
# # capabilities = webdriver.DesiredCapabilities.CHROME
# # prox.add_to_capabilities(capabilities)
# options.Proxy = prox
# options.add_argument("ignore-certificate-errors")


# PROXY = ""
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--proxy-server=%s' % PROXY)


def scroller(init_time, dir):
    item = 0
    message_tab = driver.find_element_by_class_name('_11liR')
    message_tab.click()
    if dir == "top":
        # time.sleep(3)
        message_tab.send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(4)
        message_tab.send_keys(Keys.CONTROL + Keys.HOME)
    else:
        message_tab.send_keys(Keys.CONTROL + Keys.END)
        time.sleep(1)
        message_tab.send_keys(Keys.CONTROL + Keys.END)
    # item = len(messages_details) - 1

    message_details = driver.find_elements_by_xpath('//div[@class="_1bR5a"]/div[contains(@class,"copyable-text")]')
    # # driver.execute_script("arguments[0].scrollIntoView();", messages_details[item])
    item = 0 if dir == "top" else len(message_details) - 1
    message_time = message_details[item].get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
    # print(dir)
    # time.sleep(2)
    # print(datetime.datetime.strptime(message_time, '%H:%M'), datetime.datetime.strptime(init_time, '%H:%M'))
    if datetime.datetime.strptime(message_time, '%H:%M') == datetime.datetime.strptime(init_time, '%H:%M'):
        return
    scroller(message_time, dir)


def data_fetcher(messages_detail):
    init_time_bottom = messages_detail[len(messages_detail) - 1].get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
    scroller(init_time_bottom, "bottom")

    messages_details = driver.find_elements_by_xpath('//div[@class="_1bR5a"]/div[contains(@class,"copyable-text")]')
    messages = driver.find_elements_by_xpath(
        '//div[contains(@class,"copyable-text")]/div[@class="_3ExzF"]/span[contains(@class,"copyable-text")]')

    latest_row = ""
    with open("messagedata.csv", 'r') as f:
        for row, i in zip(reversed(list(csv.reader(f))), range(0, 1)):
            latest_row = (",".join(row))

    latest_date = latest_row.split(",")[1]
    latest_time = latest_row.split(",")[2]

    with open("messagedata.csv", 'a+') as f:
        for message, detail in zip(messages, messages_details):
            message_time = detail.get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
            message_date = detail.get_attribute("data-pre-plain-text").split(", ")[1].split("]")[0]
            user = detail.get_attribute("data-pre-plain-text").split("] ")[1].split(":")[0]
            # print(datetime.datetime.strptime(message_time, '%H:%M'), datetime.datetime.strptime(latest_time, '%H:%M'),datetime.datetime.strptime(latest_date, '%d/%m/%Y'), datetime.datetime.strptime(message_date,'%d/%m/%Y'))
            # print(message_date,message_time,latest_date,latest_time)
            if latest_date == "Date":
                print(message.text, detail.get_attribute("data-pre-plain-text"))
                f.write(user + "," + message_date + "," + message_time + "," + message.text + "," + "\n")

            elif datetime.datetime.strptime(latest_date, "%d/%m/%Y") <= datetime.datetime.strptime(message_date,
                                                                                                   "%d/%m/%Y") and datetime.datetime.strptime(
                message_time, "%H:%M") > datetime.datetime.strptime(latest_time, "%H:%M"):
                print(message.text, detail.get_attribute("data-pre-plain-text"))
                f.write(user + "," + message_date + "," + message_time + "," + message.text + "," + "\n")

def whatsapp_data_fetcher(driver,group_name,*args,**kwargs):
    t_out = 20
    try:
        element_pres = EC.presence_of_element_located((By.XPATH, '//div[@title="Menu"]'))
        WebDriverWait(driver, t_out).until(element_pres)
        # print("found")
        group_select = driver.find_element_by_xpath("//span[@title=" + group_name + "]")
        # print(group_select)
        group_select.click()

        t_out = 5

        try:
            element_pres = EC.presence_of_element_located((By.XPATH,
                                                           '//div[contains(@class,"copyable-text")]/div[@class="_3ExzF"]/span[contains(@class,"copyable-text")]'))
            WebDriverWait(driver, t_out).until(element_pres)
            # messages_tab = driver.find_element_by_xpath('//div[@class="_11liR"]')
            messages_details = driver.find_elements_by_xpath(
                '//div[@class="_1bR5a"]/div[contains(@class,"copyable-text")]')
            # messages = driver.find_elements_by_xpath(
            #     '//div[@class="copyable-text"]/div[@class="_3ExzF"]/span[contains(@class,"copyable-text")]')

            if not os.path.isfile("./messagedata.csv"):
                init_time_top = messages_details[0].get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
                scroller(init_time_top, "top")
                with open("messagedata.csv", 'a') as f:
                    f.write("User,Date,Time,Message\n")

            data_fetcher(messages_details)
        except TimeoutException:
            print("field not found")

    except TimeoutException:
        print("User not logged in")

class MessageListener(AbstractEventListener):
    def __init__(self,group_name):
        self.group_name=group_name

    def before_click(self, element, driver):
        element=element.find_element_by_xpath("./../../..").find_element_by_xpath('//div[@class="_1SjZ2"]/div[@class="_15smv"]')
        print(element.get_attribute("class"))
        if len(element.text)!=0:
            print("before_click %s" % element.get_attribute("class"))
            whatsapp_data_fetcher(driver, self.group_name)

    # def before_change_value_of(self, element, driver):
    #     print("before_change_value_of")
    #     if element.get_attribute("class")=="TbtXF" and element.find_element_by_xpath('//div[@class="_2pkLM"]/div/span').get_attribute("title")==self.group_name.split("\"")[1].split("\"")[0]:
    #         whatsapp_data_fetcher(driver, self.group_name)

def activecheck(*args):
    print(args[0])
    return False if args[0] == Key.esc else True
if __name__=="__main__":
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = "http://web.whatsapp.com/"
    group_name = "\"Test group\""

    # driver = EventFiringWebDriver(driver, MessageListener())
    driver = EventFiringWebDriver(driver, MessageListener(group_name))
    driver.get(url)
    # driver.execute_script(
    #     "var options = { childList:true }; const observer = new MutationObserver(arguments[1]); observer.observe(arguments[0],options);",
    #     driver.find_element_by_xpath('//div[@class="_2aBzC"]'), whatsapp_data_fetcher)

    whatsapp_data_fetcher(driver,group_name)
    # driver.back()
    # with Listener(on_press=activecheck) as listener:
    #     listener.join()


