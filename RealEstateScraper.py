""" Sources I consulted 
https://blog.scrapinghub.com/2016/06/22/scrapy-tips-from-the-pros-june-2016 (infinite scroll)
http://chromedriver.chromium.org/
https://stackoverflow.com/questions/39112138/use-selenium-to-click-a-load-more-button-until-it-doesnt-exist-youtube #How I solved the more button issue at the bottom
#stackoverflow.com (in general)
"""
#################################################################################
"""
PREREQ please make sure you have ChromeDriver installed  http://chromedriver.chromium.org/  AND Your Chrome app is up to date. 
NOTE it IF YOU ARE using Spyder the .exe needs to go in your anaconda/bin folder. 
"""
#Libraries
from selenium import webdriver  
import time
from bs4 import BeautifulSoup
#import requests 
import pandas as pd
import os
#import numpy as np
#from tabulate import tabulate if we wanted it to print out the df in terminal

#Set your working directory here please
os. chdir("/Users/fire/Desktop/")
    

#We will be scraping my counties real estate records.  This can be done for a numebr of counties across VA, but just doing mine as I can validate easily 
URL = 'http://vamanet.com/cgi-bin/MAPSEARCH2?LOCAL=TAZ&ORDER=NAM&LSTNAM=&FSTNAM=&INMAP=&ININS=&INDCIR=&INBLOCK=&INLOT=&ADDNUM=&ADDST=&RECNUM=0&TYPE=ALL&NORECS=999'

driver = webdriver.Chrome()
driver.get(URL)

soup=BeautifulSoup(driver.page_source, 'lxml')

datalist = [] #empty list
x = 0 


while True:
    
    try:
        #Beautiful soup takes over here to wrangle the HTML
        soup_level2=BeautifulSoup(driver.page_source, 'lxml')

        #Beautiful Soup grabs the HTML table on the page
        table = soup_level2.find_all('table')[1]
        
        #Giving the HTML table to pandas to put in a dataframe object
        df = pd.read_html(str(table),header=1)
        
        #Stores the dataframes in a list
        datalist.append(df[0])
        
        #increse the counter 
        x += 1
        
        loadMoreButton = driver.find_element_by_xpath('/html/body/table[2]/tbody/tr[2]/td/center/a') #defines the button to load the next page/table
        time.sleep(2)
        loadMoreButton.click() #The actual click
        time.sleep(5)
        
    except Exception as e:
        print (e)
        break
    
print ("Complete")

time.sleep(30) #If this is smaller it will cause all the data not to load. 

driver.quit()

#combines all the dataframes in the list into one big dataframe
result=pd.concat(datalist)

#Prints to the command line if that is what you are using. 
#converts to an ascii table
#print(tabulate(result, headers=["Employee Name","Job Title","Overtime Pay","Total Gross Pay"],tablefmt='psql'))

#Grabs your current working directory. Low key probably the best trick I learned from this assignment 
path = os.getcwd()

#open, write, and close the file
f = open(path + "\export_dataframe.csv","w") 
f.write(result)
f.close()


#exports the data frame to an excel file
export_csv = result.to_csv (path + "\export_dataframe.csv", index = None, header=True) #Don't forget to add '.csv' at the end of the path


##################################################################################
""" Starts analysis """ 
#Going to list usefule information from the perspective of an investor as well as a real estate Agent 

#path = os.getcwd()  #Run this IF you come back and do this in sections as opposed to ctrl A run

data = pd.read_csv(path + "\export_dataframe.csv") 

#What is the highest value building in the county? #What about Residential property?
data.loc[data['Value'].idxmax()]  #The local college, makes sense since they have sport arena's 

data.loc[data['Value'][data['Type'] == 'Dwelling'].idxmax()] #Makes sense since this is farm land spanning most of the areas highway

#Lets group by type and get sthe average value of a property by its type
#Then lets get the count so we can see how representitive the averages are
data.groupby('Type')['Value'].mean()
data.groupby('Type')['Value'].count()

##Lets get the average acres by type 
#Then lets get the sum of all the Acres We could then check this against data online to see if they are tracking everything
data.groupby('Type')['Acres'].mean()
data.groupby('Type')['Acres'].sum()
data['Acres'].sum() #44,351.9883 Google says 333,000 acres interesting. 
                    # Too many NA's for this imo 

#lets Find the average price per acre for the county based on Type of real estate
    #Generally people look at price per sqft, but I believe in more rural areas 
    #the measurement based on line tends to be more representative. 
sumprice=data.groupby('Type')['Value'].sum()
sumsqac=data.groupby('Type')['Acres'].sum()
avepricesqacre=round(sumprice/sumsqac)  
#These look right besides for Apartmnet. The NA's with the value are probably throwing it off
#The town houses also appear wrong probably because they aren't common here. 

#Lets look at Owners name and see who owns a ton of property. Generally this will mean they can teach new investors, 
    #or they would be open to seller financing the sell of one of their properties
counts = data['Owners Name'].value_counts()
data[data['Owners Name'].isin(counts.index[counts > 1])] #this subsets the df showing anyone whos name appears more than once

#This groups by then shows a sorted list of who owns the most. 
propertiesOwned = data.groupby('Owners Name')['Owners Name'].count()
propertiesOwned[propertiesOwned > 2].sort_values(ascending=False)

#Final one lets see how many LLC's businesses etc are property owners
data[data['Owners Name'].str.contains("Llc")].nunique()#73 
