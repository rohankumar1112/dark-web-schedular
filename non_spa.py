from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from bs4 import BeautifulSoup
from databaseConnection import collection2
from datetime import date
import pymongo
import time


def scroll(driver):
    reached_page_end = False
    last_height = driver.execute_script("return document.body.scrollHeight")
    while not reached_page_end:
        driver.find_element(By.XPATH,'//body').send_keys(Keys.END)   
        time.sleep(10)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
                reached_page_end = True
        else:
                last_height = new_height

def press_next_btn(driver,xpath_of_next_btn) :
    try :
        time.sleep(10)
        next_btn = driver.find_element(By.XPATH,str(xpath_of_next_btn))
        if next_btn.is_enabled or next_btn.is_displayed  and not 'link-unactive' in next_btn.get_attribute('class') :
            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
            time.sleep(10)
            next_btn.click()
            return True
        else :
            return False

    except NoSuchElementException:
        return False
    except ElementNotInteractableException:
        return False

def no_next_btn(driver,i,xpath_of_pagination_container,tag_name_of_pages) :
    time.sleep(10)
    pagination_container = driver.find_element(By.XPATH,str(xpath_of_pagination_container))
    all_pages = pagination_container.find_elements(By.TAG_NAME,str(tag_name_of_pages))
    if len(all_pages) == i :
        return False
    next_page = all_pages[i]
    driver.execute_script("arguments[0].scrollIntoView();", next_page)
    next_page.click()
    return True                

def scroll(driver):
    reached_page_end = False
    last_height = driver.execute_script("return document.body.scrollHeight")
    while not reached_page_end:
        driver.find_element(By.XPATH,'//body').send_keys(Keys.END)   
        time.sleep(10)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
                reached_page_end = True
        else:
                last_height = new_height

def scrap_nonSpa(driver,post_links,title_xpath,body_xpath,date_xpath):
    for lnk in post_links:
        try:
            driver.get(lnk)
            time.sleep(10)
        except:
            pass    
        temp = ''
        try:
            title = driver.find_element(By.XPATH, title_xpath)
            element_html=title.get_attribute('outerHTML')
            title=BeautifulSoup(element_html,'html.parser')
            title=title.text
            temp += title+' '
            
        except:
            title='Not found'

        try:
            for xp in body_xpath:
                try:
                    bodys = driver.find_elements(By.XPATH, xp)
                    for body in bodys:
                        element_html=body.get_attribute('outerHTML')
                        body=BeautifulSoup(element_html,'html.parser')
                        temp += body.text+' '   
                except:
                    pass        
            body_data=temp
        except:
            body_data='Not found'

        try:
            if date!=None:
                date = driver.find_element(By.XPATH, date_xpath)
                element_html=date.get_attribute('outerHTML')
                date=BeautifulSoup(element_html,'html.parser')
                date=date.text
            else:
                date=None    
        except:
            date='Not found'


        if title !='Not found':
            db_dict = {'Title': title, 'Body': body_data, 'Date': date, 'Url': lnk}
            existing_data = collection2.find_one({'Title': title})
            print(db_dict)
            if existing_data:

                if existing_data['Body'] != body_data or existing_data['Date'] != date:
                    update_query = {'$set': {'Body': body_data, 'Date': date, 'Url': lnk}}
                    collection2.update_one({'Title': title}, update_query)
            else:
                collection2.insert_one(db_dict)
        else:
            print("Data not fetched!!")        

def Non_spa(darkweb_url, iterator, title_xpath, body_xpath,date_xpath=None,scrollable=False,clickable=False,clickable_btn_xpath=None,pagination = False,is_nextbtn=True,xpath_of_next_btn=None,xpath_of_pagination_container=None,tag_name_of_pages=None,waitTime=10):

    with TorBrowserDriver("/home/rohan/Downloads/tor-browser-linux64-12.0.1_ALL/tor-browser") as driver:
 
        driver.maximize_window()
        driver.get(darkweb_url)
        time.sleep(waitTime)

        if scrollable==True:
            scroll(driver)

        while clickable == True :
            if clickable_btn_xpath!=None:
                clickable = press_next_btn(driver,clickable_btn_xpath)

        perv_url=None
        post_links=[]
        if pagination == True:
            i=0
            while pagination == True :

                post_link=driver.find_elements(By.XPATH,iterator)
                for inside_lnk in post_link:
                    try:
                        lnk=inside_lnk.get_attribute('href')
                        if lnk !='#' and lnk!=None:
                            post_links.append(lnk) 
                    except:
                        pass
                    try:
                        lnk2=inside_lnk.get_attribute("onclick")
                        ind=lnk2.index("'")
                        temp_link=""
                        for i in range(ind+1,len(lnk2)):
                            if lnk2[i]!="'":
                                temp_link+=lnk2[i]
                            else:
                                break
                        if temp_link!="" and lnk2 !=None:
                            lnk=  darkweb_url + temp_link
                            post_links.append(lnk)
                    except: 
                        pass
                    

                if is_nextbtn == True and xpath_of_next_btn!=None:

                    curr_url=driver.current_url
                    if curr_url==perv_url:
                        break
                    else:
                        perv_url=curr_url

                    pagination = press_next_btn(driver,xpath_of_next_btn)
                    if pagination==False:
                        break

                if is_nextbtn == False and xpath_of_pagination_container!=None and tag_name_of_pages!=None:
                    i = i + 1
                    pagination = no_next_btn(driver,i,xpath_of_pagination_container,tag_name_of_pages)
                    if pagination==False:
                        break
        else:
            post_link=driver.find_elements(By.XPATH,iterator)
            for inside_lnk in post_link:
                try:
                    lnk=inside_lnk.get_attribute('href')
                    if lnk !='#' and lnk!=None:
                        post_links.append(lnk) 
                except:
                    pass
                try:
                    lnk2=inside_lnk.get_attribute("onclick")
                    ind=lnk2.index("'")
                    temp_link=""
                    for i in range(ind+1,len(lnk2)):
                        if lnk2[i]!="'":
                            temp_link+=lnk2[i]
                        else:
                            break
                    if temp_link!="" and lnk2 !=None:
                        lnk=  darkweb_url + temp_link
                        post_links.append(lnk)
                      
                except:
                    pass 

        if len(post_links)>0:
            scrap_nonSpa (driver,post_links,title_xpath,body_xpath,date_xpath)   

        driver.close()