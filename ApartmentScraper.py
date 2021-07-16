#!/usr/bin/env python3

# Author: Jasper Hawks
# 
# ArgumentScraper the file that handles
# scraping apartments.com for listings
# and exporting them to a spreadsheet

import argparse # Import argparse because eventually I want everything to be handled with commands
import xlwt # Import xlwt to write to spreadsheets
from xlwt import Workbook # Import the workbook function of xlwt
import requests # Import requests so we can request from the Apartments.com site
from bs4 import BeautifulSoup # Import Beautiful Soup to scrape data from the site
import re # Import re so we can use regex

tr = 0 # Instantiate the title row variable
ar = 0 # Instantiate the address row variable
pr = 0 # Instantiate the price row variable
br = 0 # Instantiate the beds row variable
availr = 0 #Instantiate the available row variable
amsr = 0 # Instantiate the amenities row variable
sqr = 0 # instantiate the square feet row variable
linkr = 0 # Instantiate the link row variable


# Instantiate a parser so that we can use positional arguments on the command line
parser = argparse.ArgumentParser(description="Scrapes Apartments.com for different apartment listings then exports the contents to an Excel file.")

# Add arguments to the parser starting with the name of the argument, the nargs which allows optional or required arguments, the type then the help text.
parser.add_argument("Region", metavar="Region",type=str,help="The name of the region you would like to search for apartments in separated by -. The formatting should be region, city, and state abbreviation. For example Downtown-Norfolk-Norfolk-VA. You can also search by city alone. For example Virginia-Beach-VA.")
parser.add_argument("--minB",nargs="?",type=int,help="Minimum amount of beds",default=-1)
parser.add_argument("--maxB",nargs="?",type=int,help="Maximum amount of beds",default=-1)
parser.add_argument("--minP",nargs="?",type=int,help="Minimum amount of prices",default=-1)
parser.add_argument("--maxP",nargs="?",type=int,help="Maximum amount of prices",default=-1)

# Then args will store all of our arguments so that we can use them throughout the program
args = parser.parse_args()

# The Anatomy of Apartments.com is as follows:
# Apartments url/region/bedrooms-price/page number
# For example:
# https://www.apartments.com/san-francisco-ca/3-bedrooms-1225-to-1700/2


def main(): # Function that starts the rest of the program and sets things up

    minBeds = 0 # Variable for min bedrooms
    maxBeds = 0 # Variable for max bedrooms
    minPrice = 0 # Variable for min price
    maxPrice = 0 # Variable for max price
    minBedVal = False # Variable to see if we have a minBedVal
    maxBedVal = False # Variable to see if we have a maxBedVal
    minPriceVal = False# Variable to see if we have a minPriceVal
    maxPriceVal = False# Variable to see if we have a maxPriceVal

    wb = Workbook() # Instantiate the workbook
    apts = wb.add_sheet("Apartments") # Instantiate a sheet named apts that we will write data to

    userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
    headers = {"User-Agent":userAgent}
    # These two lines spoof our user agent since apartments.com filters requests by user agent

    region = args.Region # Get the region from the user

    minBeds = args.minB

    if minBeds <= 0:
        minBeds = ""

    maxBeds = args.maxB 

    if maxBeds <= 0:
        maxBeds = ""

    try:
        if minBeds > maxBeds:
            print("Invalid amount of beds")
            exit()

    except TypeError:
        pass

    minPrice = args.minP

    if minPrice <= 0:
        minPrice = ""

    maxPrice = args.maxP

    if maxPrice <= 0:
        maxPrice = ""

    try:
        if minPrice > maxPrice:
            print("Invalid minimum price")
            exit()
    except TypeError: 
        pass

    # This portion of the code base converts the inputs into data
    # that we can insert into the URL

    if type(minPrice) is int: # If the price is an int
        minPriceVal = True # Then set the minimumPriceValue to true
    if type(maxPrice) is int:
        maxPriceVal = True

    # These statements format the prices the way that Apartments.com formats them
    if minPriceVal is True and maxPriceVal is True:

        # If we have a range format it this way
        price = str(minPrice) + "-to-" + str(maxPrice)

    elif minPriceVal is True and maxPriceVal is False:

        # Just the minimum price format it this way
        price = "over-" + str(minPrice)

    elif minPriceVal is False and maxPriceVal is True:

        # Just the maximum price format it this way
        price = "under-" + str(maxPrice)

    else:
        # Otherwise leave it blank
        price = ""

    # Repeat this with beds

    if type(minBeds) is int:
        minBedVal = True
    if type(maxBeds) is int:
        maxBedVal = True

    if minBedVal is True and maxBedVal is True:

        beds = str(minBeds) + "-to-" + str(maxBeds) + "-bedrooms-"

    elif minBedVal is True and maxBedVal is False:

        beds = "min-" + str(minBeds) + "-bedrooms-"

    elif minBedVal is False and maxBedVal is True:

        beds = "max-" + str(maxBeds) + "-bedrooms-"

    else:
        beds = ""

    # getPages will return an int with a value that will act as the range for the for loop
    for i in range(getPages(region,headers,beds,price)):
        # Once we have the amount of pages we have to scrape
        # we use that as an argument in the url to change
        # pages
        scrapeSave(headers,apts,wb,region,i+1,price,beds)
        print("Page " + str(i + 1) + ": Done")

    # Place the headers on top of the columns
    apts.write(0,0,"Apartment Complex")
    apts.write(0,1,"Address")
    apts.write(0,2,"Price")
    apts.write(0,3,"Beds")
    apts.write(0,4,"Availability")
    apts.write(0,5,"Square Feet")
    apts.write(0,6,"URL")
    apts.write(0,8,"Thanks for using Apartment Scraper. Check out more of my projects on my website: https://jasperhawks.netlify.app/")

    wb.save(region + " Apartments.xls") # Save the worksheet as the region name + apartments.xls

def scrapeSave(headers,apts,wb,region,page,p,beds): # Function that scrapes the majority of the content

    # Append arguments to the url
    r = requests.get("https://www.apartments.com/" + region +"/" + beds +  p + "/" +  str(page)+ "/",headers=headers).text
    soup = BeautifulSoup(r,"html.parser") 

    for titles in soup.find_all(class_ = "js-placardTitle title"): # Find all divs with this class
        global tr
        tr += 1 # Increment the title row variable
        apts.write(tr,0,titles.text) # Write the data to the spreadsheet

    # This is repeated for all items
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
        moreinfo(links['href'],apts,wb,headers)

    for avail in soup.find_all(class_ = "availability"):
        if re.search("unavailable",avail.text):
           break
        else:
            global availr
            availr += 1
            apts.write(availr,4,avail.text)

def moreinfo(link,apts,wb,h): # This function gets the square footage
   r = requests.get(link,headers=h).text # Use the link we used previously
   soup = BeautifulSoup(r,"html.parser")

   c = 0 # Instantiate a counter variable
   for sq in soup.find_all(class_ = "rentInfoDetail"): # Find the four boxes with different data
       if re.search("sq",sq.text): # If the data has sq in its text
           global sqr
           sqr += 1 # Increment the square footage row variable
           sqclean = re.sub("\n[\d]\b.*\n","",sq.text) # Remove the title text
           apts.write(sqr,5,sqclean) # Write the rest to the cell
       else: # Otherwise
           c += 1 # Instantiate the counter variable
           if c == 4: # Since there are four boxes if we go through all four
               sqr += 1 # Increment the square footage variable by one
               apts.write(sqr,5,"Square footage not listed") # Write Square footage not listed to the cell
               c = 0 # Reset the counter variable

def getPages(reg,head,b,p): # Function to get the number of pages we have to scrape
    reg = re.sub("\b(\s)\b","-",reg) # substitute whitespace for -
    r = requests.get("https://www.apartments.com/" + reg + "/" + b + p,headers=head).text # Append the region, price, and beds to the url
    soup = BeautifulSoup(r,"html.parser")

    try:
        num = soup.find(class_ = "pageRange").text # Try to find the page range div
    except: # If there is none then we have no extra pages to scrape
        return 1 # So return one for the first page

    # Since the page range is formatted Page 1 of X then we have to use regex to get rid of the Page 1 of
    num = re.sub("^\S*\s\d*....","",num)
    return int(num) # Return the int

if __name__ == "__main__":
    main()
