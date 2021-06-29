import xlwt
from xlwt import Workbook
import requests
from bs4 import BeautifulSoup
import re

tr = 0 # Instantiate the title row variable
ar = 0 # Instantiate the address row variable
pr = 0 # Instantiate the price row variable
br = 0 # Instantiate the beds row variable
availr = 0 #Instantiate the available row variable
linkr = 0 # Instantiate the link row variable

# The Anatomy of Apartments.com is as follows:
# Apartments url/region/bedrooms-price/page number
# For example:
# https://www.apartments.com/san-francisco-ca/3-bedrooms-1225-to-1700/2

def main(): # Function that starts the rest of the program and sets things up

    minBeds = 0 # Variable for min bedrooms
    maxBeds = 0 # Variable for max bedrooms
    minPrice = 0 # Variable for min price
    maxPrice = 0 # Variable for max price

    wb = Workbook()
    apts = wb.add_sheet("Apartments")

    userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
    headers = {"User-Agent":userAgent}
    # These two lines spoof our user agent since apartments.com filters requests by user agent


    # TODO Replace all input methods with command line
    # arguments

    #TODO Eventually we will convert the mins and maxes to strings and then pass them to the Scrape Save function
    # for now we should focus on basic functionality
    region = input("Region:") # Get the region from the user
    for i in range(getPages(region,headers)):
        scrapeSave(headers,apts,wb,region,i+1)
        print("done")

    # Place the headers on top of the columns
    apts.write(0,0,"Apartment Complex")
    apts.write(0,1,"Address")
    apts.write(0,2,"Price")
    apts.write(0,3,"Beds")
    apts.write(0,4,"Availability")
    apts.write(0,5,"URL")

    wb.save(region + " Apartments.xls")

def scrapeSave(headers,apts,wb,region,page):
    region = re.sub("\b(\s)\b","-",region) # Substitute whitespace for -
    r = requests.get("https://www.apartments.com/" + region +"/" + str(page)+ "/",headers=headers).text # Append the region to the url
    soup = BeautifulSoup(r,"html.parser")

    #TODO Figure out if we want to stop the program when
    # we reach unavailable apartments. Apartments.com does
    # not list apartments from available to unavailable
    # so this could be impossible

    for titles in soup.find_all(class_ = "js-placardTitle title"):
        global tr
        tr += 1
        apts.write(tr,0,titles.text)

    for adresses in soup.find_all(class_ = "property-address js-url"):
        global ar
        ar += 1
        apts.write(ar,1,adresses.text)

    for prices in soup.find_all(class_ = "price-range"):
        global pr
        pr += 1
        apts.write(pr,2,prices.text)

    for beds in soup.find_all(class_ = "bed-range"):
        global br
        br += 1
        apts.write(br,3,beds.text)

    for avail in soup.find_all(class_ = "availability"):
        global availr
        availr += 1
        apts.write(availr,4,avail.text)

    for links in soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['property-link']):
        global linkr
        linkr += 1
        apts.write(linkr,5,links['href'])


#TODO getPages will also have to have all of the
# apartment info such as rooms and price passed to
# it as well
def getPages(reg,head):
    reg = re.sub("\b(\s)\b","-",reg) # Substitute whitespace for -
    r = requests.get("https://www.apartments.com/" + reg,headers=head).text # Append the region to the url
    soup = BeautifulSoup(r,"html.parser")

    num = soup.find(class_ = "pageRange").text
    num = re.sub("^\S*\s\d*....","",num)
    return int(num)

if __name__ == "__main__":
    main()
