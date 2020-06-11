cd C:\Users\star\Downloads\
use data.dta, clear

la var timestamp "yyyymmddhh"
gen year=substr(timestamp,1,4) 
gen month=substr(timestamp,5,2)
gen day=substr(timestamp,7,2)
gen hour=substr(timestamp,9,2)
destring year month day hour, replace

bysort year hour pca_abbrev:egen hourly_mean=mean(load_mw)
gen dateid=mdy(month, day, year)
format dateid %td
bysort dateid pca_abbrev:egen daily_total=total(load_mw)

preserve
keep if pca_abbrev=="SG"
duplicates drop dateid, force
twoway (scatter daily_total dateid),scheme(s2manual) graphregion(color(white)) xline(20820 21185 21550 21915) xtitle("Date") ytitle("Daily total load, mw") title("Daily total load of Singapore in 2016-2020, mw")
gr export Graph1.png, replace
restore

preserve
keep if pca_abbrev=="SG"
duplicates drop year hour, force
twoway (scatter hourly_mean hour if year==2016) (scatter hourly_mean hour if year==2017) (scatter hourly_mean hour if year==2018) (scatter hourly_mean hour if year==2019) (scatter hourly_mean hour if year==2020), scheme(s2manual) graphregion(color(white)) xtitle("Hour in UTC, SG local time=UTC+8") ytitle("Average hourly load, mw") title("Average hourly load of Singapore, 2016-2020") xline(16) legend (label(1 "2016") label(2 "2017") label(3 "2018") label(4 "2019") label(5 "2020"))
gr export Graph2.png, replace
restore

preserve
keep if pca_abbrev=="NZ"
duplicates drop dateid, force
twoway (scatter daily_total dateid),scheme(s2manual) graphregion(color(white)) xline(20820 21185 21550 21915) xtitle("Date") ytitle("Daily total load, mw") title("Daily total load of New Zealand in 2016-2020, mw")
gr export Graph3.png, replace
restore

preserve
keep if pca_abbrev=="NZ"
duplicates drop year hour, force
twoway (scatter hourly_mean hour if year==2016) (scatter hourly_mean hour if year==2017) (scatter hourly_mean hour if year==2018) (scatter hourly_mean hour if year==2019) (scatter hourly_mean hour if year==2020), scheme(s2manual) graphregion(color(white)) xtitle("Hour in UTC, NZ local standard time=UTC+12") ytitle("Average hourly load, mw") title("Average hourly load of New Zealand, 2016-2020") xline(12) legend (label(1 "2016") label(2 "2017") label(3 "2018") label(4 "2019") label(5 "2020"))
gr export Graph4.png, replace
restore
