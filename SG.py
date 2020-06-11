#-*-coding:utf-8-*-
import requests
import os
# from lxml import etree
import random
import time
import datetime
import webbrowser
import xlwt
import xlrd
import pandas as pd
import numpy as np
from numba import autojit

linklist=[]
base_date=datetime.datetime(2020,6,1)
count=0
while count<=999:
	date=(base_date-datetime.timedelta(days=7*count)).date()
	str_date=str(date)
	str_date=str_date.replace('-','')
	str_year=str_date[0:4]
	year=int(str_year)
	link='https://www.ema.gov.sg/cmsmedia/Publications_and_Statistics/Statistics/half-hourly-system-demand/'+str_year+'/'+str_date+'.xls'
	linklist.append(link)
	count=count+1
	if year<2016:
		break
all_links='\n'.join(linklist)
open('C:\\Users\\star\\Desktop\\all_links.txt','a').write(all_links)

ChromePath = r'C:\\Users\\star\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser(ChromePath))

for link in linklist:
	time.sleep(1+random.uniform(0,5))
	webbrowser.get('Chrome').open(link,new=2, autoraise=True)

# Check whether we have downloaded ALL required files:

filelist=os.listdir('C:\\Users\\star\\Downloads\\Singapore\\')
downloaded_list=[]
for file in filelist:
	downloaded_date=file[0:8]
	downloaded_list.append(downloaded_date)
downloaded_list.sort(reverse=True)

for i in range(0,len(downloaded_list)-1):
	downloaded_date=downloaded_list[i]
	downloaded_date1=downloaded_list[i+1]
	year=int(downloaded_date[0:4])
	month=int(downloaded_date[4:6])
	day=int(downloaded_date[6:8])
	year1=int(downloaded_date1[0:4])
	month1=int(downloaded_date1[4:6])
	day1=int(downloaded_date1[6:8])
	interval= datetime.datetime(year,month,day)-datetime.datetime(year1,month1,day1)
	interval=interval.days
	if interval!=7:
		print(interval, year, month, day)
# The xls version of 20160111 is not available (404 page not found). I downloaded its pdf version and converted to xls.
# Damaged link: https://www.ema.gov.sg/cmsmedia/Publications_and_Statistics/Statistics/half-hourly-system-demand/2016/20160111.xls
# Useful link (pdf version): https://www.ema.gov.sg/cmsmedia/Publications_and_Statistics/Statistics/half-hourly-system-demand/2016/20160111.pdf

# Unill here, I have all data files of Singapore.
# Then check whether they have the same formats or not: check their rows*columns using Python, and manually check some of them.

nrowslist=[]
ncolslist=[]
for file in filelist:
	filename='C:\\Users\\star\\Downloads\\Singapore\\'+file 
	table = xlrd.open_workbook(filename).sheet_by_index(0)
	nrows = table.nrows
	nrowslist.append(nrows)
	ncols = table.ncols
	ncolslist.append(ncols)

for i in range(0,len(nrowslist)-1):
	if nrowslist[i+1]!=nrowslist[i]:
		print('something wrong')
		print(filelist[i], filelist[i+1])

for i in range(0,len(ncolslist)-1):
	if ncolslist[i+1]!=ncolslist[i]:
		print('something wrong')
		print(filelist[i], filelist[i+1])

# Confirmed that they have the same formats. Then process these small files to one large file:
# -- suppose we are focusing on the "Actual System Demand" in each day
# Singapore is at UTC+8 -- no daylight saving issues.

# For each week's small file, convert it to a 168*2 matrix: 168 rows for 24 hours in 7 days, and 2 columns for timestamp and actual system load (MW).
# The original dataset is half-hour based; therefore, hourly data comes from the sum of 2 half-hour periods.
# Date will be dd-mm-yyyy in the final dataset (although yyyy-mm-dd in the coding process).

@autojit
def process_from(path):
	filelist=os.listdir(path)
	for file in filelist:
		filename=path+file 
		table = xlrd.open_workbook(filename).sheet_by_index(0)
		starting_date=datetime.datetime(int(file[0:4]),int(file[4:6]),int(file[6:8]))
		weekly_data = np.zeros(shape=(168,2))
		count=1
		hourly_total_list=[]
		for day in range(0,7):
			str_date=str((starting_date+datetime.timedelta(days=day)).date()).replace('-','')
			int_date=int(str_date)
			for period in range(0,24):
				hourly_total=table.cell(period*2+5,day*3+1).value+table.cell(period*2+6,day*3+1).value
				row=period+day*24
				# Now the time and dates are based on Singapore local time UTC+8 (sg_).
				# Convert to UTC+0:
				sg_timestamp=datetime.datetime(int(str_date[0:4]),int(str_date[4:6]),int(str_date[6:8]),period)
				# Now sg_timestamp indicates the starting time of each slot.
				utc_timestamp=str(sg_timestamp-datetime.timedelta(hours=8))
				utc_timestamp=utc_timestamp.replace('-','')
				utc_timestamp=utc_timestamp.replace(' ','')
				utc_timestamp=utc_timestamp.replace(':','')
				utc_timestamp=utc_timestamp[0:10]
				weekly_data[row][0]=int(utc_timestamp)
				weekly_data[row][1]=hourly_total
		dta_data = pd.DataFrame({'timestamp': weekly_data[:, 0], 'load_mw': weekly_data[:, 1]})
		dta_data.to_stata('C:\\Users\\star\\Downloads\\Singapore_dta\\'+file[0:8]+'.dta')

process_from('C:\\Users\\star\\Downloads\\Singapore\\')

# Then process the dta files in STATA. I will generate some STATA command using Python loops, and save the commands in "commands.txt"

filelist=os.listdir('C:\\Users\\star\\Downloads\\Singapore_dta\\')
commands='cd '+'C:\\Users\\star\\Downloads\\Singapore_dta'+'\n'
commands=commands+'use '+filelist[0]+', clear \n'
commands=commands+'append using '
for i in range(1,len(filelist)):
	commands=commands+filelist[i]+' '
commands=commands+'\n'
commands=commands+'drop index \n'
commands=commands+'tostring timestamp, replace \n'
commands=commands+'gen year=substr(timestamp,1,4) \n'
commands=commands+'destring year, replace \n'
commands=commands+'keep if year>=2016 \n'
commands=commands+'save SG.dta, replace'

open('C:\\Users\\star\\Desktop\\commands.txt','a').write(commands)

# Continue Processing in STATA
