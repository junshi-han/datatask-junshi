import requests
import os
# from selenium import webdriver
# from selenium.webdriver.support.ui import Select
from lxml import etree
import random
import time
import datetime
import webbrowser
import xlwt
import xlrd
import pandas as pd
import numpy as np
import csv
# from numba import autojit

# Starting from Jan 01, 2016 and request data in 30-day non overlapping intervals.
# The website may get stuck if the interval is too large, say, 1-year interval.

start_date_list=[]
end_date_list=[]

base_date=datetime.datetime(2016,1,1)
count=0
while count<=999:
	if count==0:
		start_date=base_date
		end_date=(start_date+datetime.timedelta(days=29))
	elif count>0:
		start_date=(end_date+datetime.timedelta(days=1))
		end_date=(start_date+datetime.timedelta(days=29))
	count=count+1
	gap=end_date-datetime.datetime(2020,6,9)
	if gap.days>=0:
		break
	start_date_list.append(start_date)
	end_date_list.append(end_date)

gap=datetime.datetime(2020,6,9)-end_date_list[len(end_date_list)-1]
if gap.days>0:
	start_date_list.append(end_date_list[len(end_date_list)-1]+datetime.timedelta(days=1))
	end_date_list.append(datetime.datetime(2020,6,9))

if len(end_date_list)!=len(start_date_list):
	print("Wrong!")
elif len(end_date_list)==len(start_date_list):
	start_date8_list=[]
	end_date8_list=[]
	for i in range(0,len(start_date_list)):
		start_date8=str(start_date_list[i])
		start_date8=start_date8.replace('-','')
		start_date8=start_date8[0:8]
		start_date8_list.append(start_date8)
		end_date8=str(end_date_list[i])
		end_date8=end_date8.replace('-','')
		end_date8=end_date8[0:8]
		end_date8_list.append(end_date8)
print(len(start_date8_list))
print(len(end_date8_list))

website='https://www.emi.ea.govt.nz'

ChromePath = r'C:\\Users\\star\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser(ChromePath))

for i in range(0,len(start_date8_list)):
	pagelink='https://www.emi.ea.govt.nz/Wholesale/Reports/W_GD_C?DateFrom=20200609&DateTo=20200609&\
_rsdr=D1&_si=_dr_DateFrom|'+start_date8_list[i]+',_dr_DateTo|'+end_date8_list[i]+',_dr_RegionType|NZ,v|4'
	headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
	r=requests.get(pagelink,headers=headers)
	s=etree.HTML(r.text)
	downloadlink=s.xpath('//*[@class="dateReportDesc"]/a/@href')[0]
	downloadlink=website+downloadlink
	time.sleep(5+random.uniform(0,5))
	webbrowser.get('Chrome').open(downloadlink,new=2, autoraise=True)

# Then process these files into one file.

filelist=os.listdir('C:\\Users\\star\\Downloads\\NZ\\')

for file in filelist:
	data=open('C:\\Users\\star\\Downloads\\NZ\\'+file).readlines()
	open('C:\\Users\\star\\Downloads\\NZ_new\\'+file,'w').writelines(data[11:])
	data=pd.read_csv('C:\\Users\\star\\Downloads\\NZ_new\\'+file)
	data.to_excel('C:\\Users\\star\\Downloads\\NZ_new\\'+file[:-4]+'.xls')

filelist=os.listdir('C:\\Users\\star\\Downloads\\NZ_new\\')
for file in filelist:
	if file[-4:]=='.csv':
		os.remove('C:\\Users\\star\\Downloads\\NZ_new\\'+file)


# Now convert all times into UTC+0
# Firstly, define the cutoffs:
c1=datetime.datetime(2016,4,3,3)
c2=datetime.datetime(2016,9,25,3)
c3=datetime.datetime(2017,4,2,3)
c4=datetime.datetime(2017,9,24,3)
c5=datetime.datetime(2018,4,1,3)
c6=datetime.datetime(2018,9,30,3)
c7=datetime.datetime(2019,4,7,3)
c8=datetime.datetime(2019,9,29,3)
c9=datetime.datetime(2020,4,5,3)

filelist=os.listdir('C:\\Users\\star\\Downloads\\NZ_new\\')
for file in filelist:
	filename='C:\\Users\\star\\Downloads\\NZ_new\\'+file 
	table = xlrd.open_workbook(filename).sheet_by_index(0)
	nrows=table.nrows
	data = np.zeros(shape=(nrows-1,2))
	for row in range(1,nrows):
		start_year=int(table.cell(row,1).value[6:10])
		start_month=int(table.cell(row,1).value[3:5])
		start_day=int(table.cell(row,1).value[0:2])
		start_hour=int(table.cell(row,1).value[11:13])
		start_minute=int(table.cell(row,1).value[14:16])
		start_datetime=datetime.datetime(start_year,start_month,start_day,start_hour,start_minute)
		print(start_datetime)
		period=table.cell(row,3).value
		# Convert Daylight Saving Time (UTC+13) to UTC:
		if ((start_datetime-c1).total_seconds()<0)\
or ((start_datetime-c2).total_seconds()>0 and (start_datetime-c3).total_seconds()<0)\
or ((start_datetime-c4).total_seconds()>0 and (start_datetime-c5).total_seconds()<0)\
or ((start_datetime-c6).total_seconds()>0 and (start_datetime-c7).total_seconds()<0)\
or ((start_datetime-c8).total_seconds()>0 and (start_datetime-c9).total_seconds()<0):
			utc_timestamp=str(start_datetime-datetime.timedelta(hours=13))
		else:
			utc_timestamp=str(start_datetime-datetime.timedelta(hours=12))
		# However, 2 time slots 0200-0230 and 0230-0300 (local time) were duplicated each year:
		if ((start_year==2016) and (start_month==4) and (start_day==3) and (start_hour==2) and (period==7 or period==8))\
or ((start_year==2017) and (start_month==4) and (start_day==2) and (start_hour==2) and (period==7 or period==8))\
or ((start_year==2018) and (start_month==4) and (start_day==1) and (start_hour==2) and (period==7 or period==8))\
or ((start_year==2019) and (start_month==4) and (start_day==7) and (start_hour==2) and (period==7 or period==8))\
or ((start_year==2020) and (start_month==4) and (start_day==5) and (start_hour==2) and (period==7 or period==8)):
			utc_timestamp=str(start_datetime-datetime.timedelta(hours=12))
		utc_timestamp=utc_timestamp.replace('-','')
		utc_timestamp=utc_timestamp.replace(' ','')
		utc_timestamp=utc_timestamp.replace(':','')
		utc_timestamp=utc_timestamp[0:10]
		data[row-1][0]=int(utc_timestamp)
		data[row-1][1]=(table.cell(row,6).value)*1000
	dta_data = pd.DataFrame({'timestamp': data[:, 0], 'load_mw': data[:, 1]})
	dta_data.to_stata('C:\\Users\\star\\Downloads\\NZ_dta\\'+file[:-4]+'.dta')

# Transfer to STATA:

commands='cd C:\\Users\\star\\Downloads\\NZ_dta\\ \n'

filelist=os.listdir('C:\\Users\\star\\Downloads\\NZ_dta\\')

commands=commands+'use '+filelist[0]+', clear\n append using '
for i in range(1,len(filelist)):
	commands=commands+filelist[i]+' '

commands=commands+'\n tostring timestamp, replace \n \
gen yyyymmdd=substr(timestamp,1,8) \n\
gen starting_hour=substr(timestamp,9,2)\n \
bysort yyyymmdd starting_hour:egen hourly_load=total(load_mw) \n'
commands=commands+'duplicates drop yyyymmdd starting_hour, force\n \
drop yyyymmdd starting_hour\n \
drop index\n \
drop load_mw\n \
ren hourly_load load_mw\n \
save NZ.dta, replace\n'

open('C:\\Users\\star\\Desktop\\commands.txt','a').write(commands)

# Continue Processing in STATA
