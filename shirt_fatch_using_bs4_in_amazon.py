import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
first_url = "https://www.amazon.in/s?i=apparel&rh=n%3A1968093031&fs=true&qid=1660472656&ref=sr_pg_1"

def request_data_from_amazon_for_scraping(scrap_url):
    webpage = requests.get(scrap_url, headers=HEADERS)
    page_response = webpage.status_code
    while page_response != 200:
        webpage = requests.get(scrap_url, headers=HEADERS)
        page_response = webpage.status_code
    soup = BeautifulSoup( webpage.content , 'html.parser')
    return soup

def fatch_and_print_product_basic_details(scrap_url,count,soup):
    Filter_multiple_class = re.compile("sg-col-4-of-12\s+s-result-item", re.I)
    product_lists = soup.find_all("div", attrs={"class": Filter_multiple_class})
    print('total products found: ',len(product_lists))
    
    total_product_list = []
    for product_list in product_lists:
        single_product_dict = {}
        
        # extract the images from the amazone
        image_outer_div = product_list.find("div", {"class": "s-image-tall-aspect"})
        image_path = image_outer_div.img
        # end of the images fatch

        # extract the brand from the product
        brand_name = product_list.find("h5", {"class": "s-line-clamp-1"}).span
        # end for brand fatch from the product

        # extract the name from the product
        product_name = product_list.find("h2", {"class": "s-line-clamp-2"}).a.span
        product_url = product_list.find("h2", {"class": "s-line-clamp-2"}).a
        pro_url ='https://www.amazon.in/'+ product_url['href']
        # end for name fatch from the product

        # extract product price
        product_price = ""
        product_Filter_multiple_class = re.compile("a-row\s+a-size-base\s+a-color-base", re.I)
        product_price = product_list.find("div", {"class": product_Filter_multiple_class})
        product_price_select = product_list.find("span", {"class": "a-price-whole"})
        final_price = None
        try:
            final_price = product_price_select.text if product_price_select.text else None
        except:
            final_price = None
        # end product price    
        
        single_product_dict['amazone_page_number']= str(count)
        single_product_dict['brand_name'] = brand_name.text
        single_product_dict['product_name'] = product_name.text
        single_product_dict['product_price'] = final_price
        single_product_dict['product_url'] = pro_url
        single_product_dict['product_img'] = image_path.attrs['src'] 
        single_product_dict['amazone_page_url']= str(scrap_url)
        total_product_list.append(single_product_dict)
    return total_product_list
        
    
first_page = 1
last_page = 3
scrap_url = ""
count = 1
df = pd.DataFrame()
print('\n+++++++++++++++++ Scrapping Start +++++++++++++++++')
for page in range(first_page,last_page+1):
    if page == 1:
        print('\n-------------- page number 1 --------------')
        scrap_url = first_url
        print('scraped page url ->',scrap_url)
        soup = request_data_from_amazon_for_scraping(scrap_url)
        total_product_list = fatch_and_print_product_basic_details(scrap_url,count,soup)
        df = pd.DataFrame(total_product_list)
    else:
        print('\n-------------- page number '+str(count)+' --------------')
        scrap_url =" https://www.amazon.in/s?i=apparel&rh=n%3A1968093031&fs=true&page="+str(count)+"&qid=1660472862&ref=sr_pg_"+str(count)
        soup = request_data_from_amazon_for_scraping(scrap_url)
        print('scraped page url ->',scrap_url)
        soup = request_data_from_amazon_for_scraping(scrap_url)
        total_product_list2 = fatch_and_print_product_basic_details(scrap_url,count,soup)
        for single_data in range(len(total_product_list2)):
            df.loc[len(df.index)] = total_product_list2[single_data]
        
    print('all the data is scraped successfully and upload.')
    count+=1

print('\n+++++++++++++++++ Scrapping End +++++++++++++++++')
df.to_excel("output.xlsx")
print('\noutput -> a file hax been generated with the name output.xlsx',)
  