#requests module will allow you to send HTTP/1.1 requests using Python. With it, you can add content like headers, form data, multipart files, and parameters via simple Python libraries. It also allows you to access the response data of Python in the same way
import requests
#csv module implements classes to read and write tabular data in CSV format
import csv
#Importing thomascookConfig file which describes about the csv file's fileds name.
import thomascookConfig

#Assigning the searching criteria(values)in a dictionary for which we want to scrap Hotels information from the ThomasCook.com website.
input_dict = {
    'city': 'Rimini',
    'country': 'Italy',
    'checkIn': "20.02.2019",
    'checkOut': "22.02.2019",
    'rooms': 1,
    'adults': 2,
    'noOfDays': 2,
}
http_proxy = "Your proxy:Port Number"
https_proxy = "Your proxy:Port Number"
proxies = {'http': http_proxy,
           'https': https_proxy}

###Hitting City_Id page to get dynamic City_Id value. So that we can search hotels for any destiation.
city_url = "https://api.thomascook.de/ajax?lieferant=TT17&format=json&authKey=e06e3b367694bb338ca9ada380a5bed0&method=getInventory&product_type=h&searchterm={0}".format(input_dict['city'].strip().replace(' ','+'))
# print(city_url)

city_url_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "api.thomascook.de",
    "Origin": "https://www.thomascook.de",
    "Referer": "https://www.thomascook.de/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
}

city_resp = requests.get(city_url,headers=city_url_headers,proxies=proxies)
# print(city_resp.status_code,city_resp.text)

city_id = None
if city_resp.status_code == 200:
    city_json_resp = city_resp.json()
    city_id = city_json_resp['cities']['items']['item'][0]['id']
# print("city_id===",city_id)

#Now Hitting List Page Url to capture all Hotels urls and store it into a list.
list_url = "https://api.thomascook.de/ajax?lieferant=TT17&format=json&authKey=e06e3b367694bb338ca9ada380a5bed0&method=getHotelsPerCity&asn=1&bis={0}&dauer={1}d&ergebnisse=10000&erwachsene={2}&position=21&produkt=h&sortierung=RECOMMENDATION_DESC&stadtId={3}&tophotels=1&von={4}".format(input_dict['checkOut'],input_dict['noOfDays'],input_dict['adults'],city_id,input_dict['checkIn'])
# print(list_url)
list_url_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "referer": "https://www.thomascook.de/",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
}
list_url_resp = requests.get(list_url,headers=list_url_headers,proxies=proxies)
# print(list_url_resp.status_code,list_url_resp.text)

#Capturing and  storing Hotels urls and Hotel's related information.
hotel_url_list = []
if list_url_resp.status_code == 200:
    list_url__json_resp = list_url_resp.json()
    for ht in list_url__json_resp['hotels']['hotel']:
        hotel_id = ht['supplier_id']
        hotel_name = ht['hotel_name']
        star_rating = ht['category']
        region_code = ht['location']['region_code']
        country_name = ht['location']['country_name']

        hotel_url_list.append({
                "id": hotel_id,
                "name": hotel_name,
                "star_rating": star_rating,
                "region_code": region_code,
                "country_name":country_name,
            }
        )
#print("hotel_url_list====",len(hotel_url_list),hotel_url_list)

with open('ThomasCook_DE.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #Calling all fileds's name from the thomascookConfig file.
    fieldnames = thomascookConfig._getFieldNameList()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for hotel in hotel_url_list:
        #Now Hitting all Hotels Url one by one.
        hotel_url = "https://api.thomascook.de/ajax?lieferant=TT17&format=json&authKey=e06e3b367694bb338ca9ada380a5bed0&method=getOffers&bis={0}&dauer={1}d&ergebnisse=1000&erwachsene={2}&hotelId={3}&position=1&produkt=h&recently_viewed_id=KFP9ALVA5SBD2PZ7&regionId={4}&sortierung=PRICE_ASC&von={5}".format(input_dict['checkOut'],input_dict['noOfDays'],input_dict['adults'],hotel['id'],hotel['region_code'],input_dict['checkIn'])
        ##print(hotel_url)
        hotel_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "api.thomascook.de",
            "Origin": "https://buchen.thomascook.de",
            "Referer": "https://buchen.thomascook.de/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        }

        hotel_resp = requests.get(hotel_url,headers=hotel_headers,proxies=proxies)
        print("\n\n\nhotel_resp",hotel_resp.status_code)
        ##print(hotel_resp.text)

        if hotel_resp.status_code == 200:
            hotel_json_resp = hotel_resp.json()
            ##Now capturing all Hotel's information and write it into a csv file.
            for hotel_room in hotel_json_resp['offers']['offer']:
                hotel_id = hotel['id']
                hotel_name = hotel['name']
                star_rating = hotel['star_rating']

                address = ''
                if hotel_json_resp['hotel']['location']['country_name']:
                    address += hotel_json_resp['hotel']['location']['country_name'] + ", "
                if hotel_json_resp['hotel']['location']['region_name']:
                    address += hotel_json_resp['hotel']['location']['region_name'] + ", "
                if hotel_json_resp['hotel']['location']['city_name']:
                    address += hotel_json_resp['hotel']['location']['city_name']

                supplier = hotel_room['tour_operator_long']
                room_type = hotel_room['room']['room_info']
                board_type = hotel_room['boarding']['board_code']
                currency = hotel_room['pricing']['@attributes']['currency']
                price = hotel_room['pricing']['total_price']
                record = {
                    'supplier': supplier,
                    'checkIn': input_dict['checkIn'],
                    'nights': input_dict['noOfDays'],
                    'pos': hotel['country_name'],
                    'city': input_dict['city'],
                    'hotel_id': hotel['id'],
                    'adults': input_dict['adults'],
                    'hotel_name': hotel['name'],
                    'latitude': '',
                    'longitude': '',
                    'board': board_type,
                    'currency': currency,
                    'star_rating': hotel['star_rating'],
                    'pathPage': '',
                    'promotion': 'NULL',
                    'promotion_desc': 'NULL',
                    'direct_Payment': 'NULL',
                    'multiple_zone_check': 'NULL',
                    'room_type': room_type,
                    'hotel_location': address.strip(),
                    'total_price': float(price),
                }

                writer.writerow(record)


