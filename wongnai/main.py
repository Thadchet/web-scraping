from function import *

def main(poi):
    driver = prepare_browser(poi)
    df = scrape_data(driver)
    df.to_csv(poi + '.csv', encoding='utf-8')
    
if __name__ == "__main__":
    main('ภูเก็ต')
    