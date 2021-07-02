import argparse
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
amsr = 0 # Instantiate the amenities row variable
sqr = 0 # instantiate the square feet row variable
linkr = 0 # Instantiate the link row variable

# Command line stuff that we can work with later #parser = argparse.ArgumentParser(description="Scrapes Apartments.com for different apartment listings then exports the contents to an Excel file.")
#parser.add_argument("strings", metavar="Region",type=list,help="The name of the region you would like to search for apartments in. The formatting should be region, city, and state abbreviation. For example Downtown Norfolk Norfolk VA. You can also search by city alone. For example Virginia Beach VA.")
#parser.add_argument("--minB",nargs="?",type=int,help="Minimum amount of beds")
#args = parser.parse_args()

# The Anatomy of Apartments.com is as follows:
# Apartments url/region/bedrooms-price/page number
# For example:
# https://www.apartments.com/san-francisco-ca/3-bedrooms-1225-to-1700/2

# BIG TODO Refractor this mess

def main(): # Function that starts the rest of the program and sets things up

    minBeds = 0 # Variable for min bedrooms
    maxBeds = 0 # Variable for max bedrooms
    minPrice = 0 # Variable for min price
    maxPrice = 0 # Variable for max price
    minBedVal = False
    maxBedVal = False
    minPriceVal = False
    maxPriceVal = False

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

    try: # Try to assign min beds to an int
        minBeds = int(input("Min Beds (Blank by default):"))
    except ValueError: # If the user leaves minBeds blank
        minBeds = "" # Make it an empty string

    try:
        maxBeds = int(input("Max Beds (Blank by default):"))
    except ValueError:
        maxBeds = ""

    try:
        if minBeds > maxBeds:
            print("Invalid amount of beds")
            exit()

    except TypeError:
        pass

    try:
        minPrice = int(input("Min Price (Blank by default):"))
    except ValueError:
        minPrice = ""

    try:
        maxPrice = int(input("Max Price (Blank by default):"))
    except ValueError:
        maxPrice = ""

    if minPrice > maxPrice:
        print("Invalid minimum price")
        exit()
    # This portion of the code base converts the inputs into data
    # that we can insert into the URL

    if type(minPrice) is int: # If the price is an int
        minPriceVal = True # Then set the minimumPriceValue to true
    if type(maxPrice) is int:
        maxPriceVal = True

    if minPriceVal is True and maxPriceVal is True: # Then if they are both true

        price = str(minPrice) + "-to-" + str(maxPrice) # price equals this string

    elif minPriceVal is True and maxPriceVal is False:

        price = "over-" + str(minPrice)

    elif minPriceVal is False and maxPriceVal is True:

        price = "under-" + str(maxPrice)

    else:
        price = ""

    if type(minBeds) is int:
        minBedVal = True
    if type(maxBeds) is int:
        maxBedVal = True

    if minBedVal is True and maxBedVal is True:

        # TODO If the program is acting strangely remove the - from bedrooms
        beds = str(minBeds) + "-to-" + str(maxBeds) + "-bedrooms-"

    elif minBedVal is True and maxBedVal is False:

        beds = "min-" + str(minBeds) + "-bedrooms"

    elif minBedVal is False and maxBedVal is True:

        beds = "max-" + str(maxBeds) + "-bedrooms"

    else:
        beds = ""

    for i in range(getPages(region,headers,beds,price)):
        scrapeSave(headers,apts,wb,region,i+1,price,beds)
        print("done")

    # Place the headers on top of the columns
    apts.write(0,0,"Apartment Complex")
    apts.write(0,1,"Address")
    apts.write(0,2,"Price")
    apts.write(0,3,"Beds")
    apts.write(0,4,"Availability")
    apts.write(0,5,"Square Feet")
    apts.write(0,6,"URL")

    wb.save(region + " Apartments.xls")

def scrapeSave(headers,apts,wb,region,page,p,beds):
    # TODO Eventually remove str from all of the passed arguments like p and beds
    region = re.sub("\b(\s)\b","-",region) # Substitute whitespace for -
    r = requests.get("https://www.apartments.com/" + region +"/" + str(beds) +  str(p) + "/" +  str(page)+ "/",headers=headers).text # Append the region to the url
    soup = BeautifulSoup(r,"html.parser")

    #TODO Figure out if we want to stop the program when
    # we reach unavailable apartments.

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

    for links in soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['property-link']):
        global linkr
        linkr += 1
        apts.write(linkr,6,links['href'])
        moreInfo(links['href'],apts,wb,headers)

    for avail in soup.find_all(class_ = "availability"):
        if re.search("Unavailable",avail.text): break
        else:
            global availr
            availr += 1
            apts.write(availr,4,avail.text)

def moreInfo(link,apts,wb,h): # This function gets info like amenities and square footage
   r = requests.get(link,headers=h).text
   soup = BeautifulSoup(r,"html.parser")

   c = 0
   # TODO Square footage isnt behaving correctly again
   for sq in soup.find_all(lambda tag: tag.name == "div" and tag.get("class") == ["priceBedRangeInfoInnerContainer"]):
       if re.search("sq",sq.text):
           global sqr
           sqr += 1
           sqClean = re.sub("\n[\D]\B.*\n","",sq.text)
           apts.write(sqr,5,sqClean)
       else:
           c += 1
           if c == 4:
               sqr += 1
               apts.write(sqr,5,"Square footage not listed")
               c = 0

def getPages(reg,head,b,p):
    reg = re.sub("\b(\s)\b","-",reg) # Substitute whitespace for -
    print("https://www.apartments.com/" + reg + "/" + b + p)
    r = requests.get("https://www.apartments.com/" + reg + "/" + b + p,headers=head).text # Append the region to the url
    soup = BeautifulSoup(r,"html.parser")

    try:
        num = soup.find(class_ = "pageRange").text
    except:
        return 1
    num = re.sub("^\S*\s\d*....","",num)
    return int(num)

if __name__ == "__main__":
    main()
