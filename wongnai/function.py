from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import requests
import time

def prepare_browser(province):
    driver = webdriver.Edge('D:\Python learing\web-scraping\driver\msedgedriver.exe')
    url = 'https://www.wongnai.com/'
    driver.get(url)
    
    accept = driver.find_elements_by_class_name('sc-fznWqX')
    accept[1].click()
    
    search = driver.find_element_by_tag_name("button")
    search.click()
    
    location = driver.find_element_by_name('displayQ')
    location.clear()
    location.send_keys(province)
    location.send_keys(Keys.ENTER)

    ## select restaurant only
    try :
        checkbox = driver.find_elements_by_class_name('sc-1tsaoc4-0.hbDspE')
        checkbox[0].click()
    except :
        pass
    return driver

def scrape_data(driver):
    
    def find_name(page_store):
        name_store = page_store.find('h1').text
        return name_store
    
    def find_categories(page_store):
        category = [e.text for e in page_store.find('div',{'class','sc-1a3arn4-2 fSEOcf'}).children]
        return category
    
    def find_rating(page_store):
        c5 = c4 = c3 = c2 = c1 = 0
        l = [c5,c4,c3,c2,c1]
        rating = page_store.find('div',{'class':'sc-1nastw3-0 bdlWei'})
        for idx,i in enumerate(rating.children,start=0) :
            l[idx] = i.find('div',{'class':'naftl5-3'}).text
        return l[4],l[3],l[2],l[1],l[0]
    
    def find_price_hours_seat(page_store):
        side = page_store.find_all('div',{'class':'_1weidWQshSdU3oH6Fm7DNW'})
        seat = None
        price_range = None
        hours = None
        for each in side:
            for e in each.children:
                if(e.span != None):
                    if(e.span.text == 'เวลาเปิดร้าน'):
                        hours = [q.text for q in e.find_all('td')]
                if(e.find('div',{'class':'_2Kc89xSc7gyXlf6l0mPvTB'}) != None):
                    if(e.find('div',{'class':'_2Kc89xSc7gyXlf6l0mPvTB'}).text == 'จำนวนที่นั่ง'):
                        seat = e.find('span',{'class':'sc-1kh6w3g-1 ghCbHF'}).text
                    if(e.find('div',{'class':'_2Kc89xSc7gyXlf6l0mPvTB'}).text == 'ช่วงราคา'):
                        price_range = e.find('span',{'class':'sc-1kh6w3g-1 ghCbHF'}).text
        return price_range,hours,seat
    
    def find_optional(page_store):
        check = {'ที่จอดรถ': None ,'Wi-Fi': None ,'รับบัตรเครดิต' : None ,'เดลิเวอรี' : None,'เหมาะสำหรับเด็กๆ' : None,'เหมาะสำหรับมาเป็นกลุ่ม' : None,
                 'แอลกอฮอล์': None ,'ดนตรีสด' : None,'สัตว์เลี้ยงเข้าได้': None,'รับจองล่วงหน้า': None,'ร้านในโรงแรม' :None , 'รับชำระด้วยคิวอาร์โค้ด' : None}
        all_option = page_store.find_all('span',{'class':'sc-1kh6w3g-10 cklKNh'})
        have_option = page_store.find_all('span',{'class':'zjgh1d-0 PMUmm sc-1kh6w3g-9 jWTTxV'})
        for each in all_option :
            check[each.text] = 0
        for has in have_option :
            check[has.next_sibling.text] = 1
        return check
    
    def find_location(page_store):
        location = page_store.find(attrs={'data-track-id':'static-map'}).find('img')
        begin_lat = location['src'].find('lat')+4
        end_lat = location['src'].find('&lon')
        begin_long = location['src'].find('lon')+4
        end_long = location['src'].find('&level')
        latitude = location['src'][begin_lat:end_lat]
        longitude = location['src'][begin_long:end_long]
        return latitude,longitude
    
    def find_phone(page_store):
        phone_num = None
        phone = page_store.find('span',{'data-track-id':'business-phone-info-icon'})
        phone_num = phone.next_sibling.text
        return phone_num
    
    def find_address(page_store):
        address = None
        addr = page_store.find('span',{'data-track-id':'business-location-info-icon'})
        address = addr.next_sibling.text
        return address
    
    def scrape_one_page(driver):
        lst = []
        data = BeautifulSoup(driver.page_source,'lxml')
        all_store = data.find('div',{'class': 'sc-195dyzv-0 fkmkTf'})
        store = driver.find_elements_by_class_name('sc-10ino0a-5')
        for i in range(len(store)):
            try :
                store[i].click()
            except StaleElementReferenceException as Exception:
                store = driver.find_elements_by_class_name('sc-10ino0a-5')
                store[i].click()
            time.sleep(4)
            try :
                page_store = BeautifulSoup(driver.page_source,'lxml')
                name_store = find_name(page_store)
                category = find_categories(page_store)
                count_rating_1,count_rating_2,count_rating_3,count_rating_4,count_rating_5 = find_rating(page_store)
                price_range,hours,seat = find_price_hours_seat(page_store)
                optional = find_optional(page_store)
                lat,lon = find_location(page_store)
                phone_num = find_phone(page_store)
                address = find_address(page_store)
                lst.append([name_store,category,price_range,hours,seat,count_rating_1,count_rating_2,count_rating_3,count_rating_4,count_rating_5,
                            lat,lon,phone_num,address]+[op for op in optional.values()])
                print(i, 'success')
            except :
                print(i , 'fail')
                pass
            
            driver.execute_script("window.history.go(-1)")
            time.sleep(4)
        next_page = driver.find_element_by_class_name('sc-fznWqX.cqRTyF')
        next_page.click()
        time.sleep(4)
        df = pd.DataFrame(lst,columns=['name','categories','price_range','hours','seat','count_rating_1','count_rating_2','count_rating_3',
                                       'count_rating_4','count_rating_5','latitude','longitude','phone_number','address']+[col for col in optional.keys()])
        return df
    
    def scrape_all(number_of_page,driver):
        df = pd.DataFrame()
        for i in range(number_of_page):
            one_page= scrape_one_page(driver)
            df = pd.concat([df,one_page])
        return df

    df = scrape_all(1,driver)
    return df