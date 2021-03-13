from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
import csv
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MessageFetcher():
    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.url = "http://web.whatsapp.com/"
        self.group_name = "\"Test group\""
        self.group_select=None
        self.driver = EventFiringWebDriver(self.driver, MessageListener(self.group_name))
        self.driver.get(self.url)

        while 1:
            try:
                self.group_finder(self.driver, self.group_name)
                time.sleep(3)
            except KeyboardInterrupt:
                break

    def group_finder(self,driver, group_name, *args, **kwargs):
        t_out = 20
        try:
            element_pres = EC.presence_of_element_located((By.XPATH, '//div[@title="Menu"]'))
            WebDriverWait(driver, t_out).until(element_pres)
            # print("found")
            self.group_select = driver.find_element_by_xpath("//span[@title=" + group_name + "]")
            # print(group_select)
        except TimeoutException:
            print("User not logged in")

    def whatsapp_data_fetcher(self,driver, group_select):
        t_out = 5
        group_select.click()
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
                self.scroller(init_time_top, "top",driver)
                with open("messagedata.csv", 'a') as f:
                    f.write("User,Date,Time,Message\n")

            self.data_fetcher(messages_details,driver)
        except TimeoutException:
            print("field not found")

    def data_fetcher(self,messages_detail,driver):
        init_time_bottom =messages_detail[len(messages_detail) - 1].get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
        self.scroller(init_time_bottom, "bottom",driver)

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

    def scroller(self,init_time, dir,driver):
        item = 0
        message_tab = driver.find_element_by_class_name('_11liR')
        message_tab.click()
        if dir == "top":
            message_tab.send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(4)
            message_tab.send_keys(Keys.CONTROL + Keys.HOME)
        else:
            message_tab.send_keys(Keys.CONTROL + Keys.END)
            time.sleep(1)
            message_tab.send_keys(Keys.CONTROL + Keys.END)

        message_details = driver.find_elements_by_xpath('//div[@class="_1bR5a"]/div[contains(@class,"copyable-text")]')
        # # driver.execute_script("arguments[0].scrollIntoView();", messages_details[item])
        item = 0 if dir == "top" else len(message_details) - 1
        message_time = message_details[item].get_attribute("data-pre-plain-text").split("[")[1].split(",")[0]
        # print(dir)
        # time.sleep(2)
        # print(datetime.datetime.strptime(message_time, '%H:%M'), datetime.datetime.strptime(init_time, '%H:%M'))
        if datetime.datetime.strptime(message_time, '%H:%M') == datetime.datetime.strptime(init_time, '%H:%M'):
            return
        scroller(message_time, dir,driver)


class MessageListener(AbstractEventListener,MessageFetcher):
    def __init__(self,group_name):
        self.group_name=group_name

    def before_find(self,by, element, driver):
        i=0
        if self.group_name == element.split("=")[1].split("]")[0]:
            # print(element)
            try:
                element=driver.find_element_by_xpath(element).find_element_by_xpath("./../../..")
                # print(element.text)
                element=element.find_element_by_xpath('./div[@class="_1SjZ2"]/div[@class="_15smv"]/span/div[@class="_2TiQe"]')
                # print(element.text)
                group_select = driver.find_element_by_xpath("//span[@title=" + self.group_name + "]")
                super().whatsapp_data_fetcher(driver, group_select)
            except:
                # print("in")
                pass

if __name__=="__main__":
    messageFetcher=MessageFetcher()

