# %% [markdown]
# # Australia rainfall probability verification data extraction
# 
# 24 March 2022
# 
# See https://anaconda.org/bfiedler/australiaverificationdata 
# 
# This notebook extends that notebook to rainfall probability data.

# %%
import numpy as np
import glob
#import matplotlib.pyplot as plt
#from IPython.core.display import HTML
#HTML( open('my_css.css').read() ) # if you don't have my_css.css, comment this line out
from datetime import datetime as dt
utc=dt.utcfromtimestamp

# %% [markdown]
# The following adds some optional HTML color style to this jupyter notebook:

# %%
%%html
<style> div.text_cell_render{background-color: #ded; font-size: 18px}
                    .rendered_html code {background-color: #ded; color: #900; font-size: 16px}
                    .rendered_html pre {background-color: #ded; color: #900; font-size: 16px} 
</style>

# %%
lookforf="DailyPoP1"
lookforc='Mean number of days of rain >= 1 mm'
# or this:
#lookforf="DailyPoP10"
#lookforc='Mean number of days of rain >= 10 mm'

# %%
# choose one
#site='09021' #Perth
site='31011' # Cairns
#site='12038' #Kalgoorlie
#---------------------
# sites below have data issues, and should be avoided
#site='97072' # Strahan
#site='94008' # Hobart
#site='86282' # Melbourne
#site='15590' # Alice Springs

# %%
#outfileext='.csv' # normally use this
outfileext='.csvx'  # for testing, so you don't overwrite good file

# %%
pdir = 'australia_study/' # the path to where you stored the grep data files

# %%
obfile=pdir+site+'obs.csv'
print(obfile)
fcstfile=pdir+site+'fcst.csv'
print(fcstfile)
climofilex='IDCJCM*'+site+'.csv' 
climofile=glob.glob(pdir+climofilex).pop()
print(climofile)

# %%
obs=open(obfile).readlines()
fcsts=open(fcstfile).readlines()
climos=open(climofile).readlines()
print('obs',len(obs))
print('fcsts',len(fcsts))
print('climos',len(climos))

# %%
nline=0
found=False

for line in climos:
    if not found: print(line,end='')
    if nline==3: sitename=line.strip().replace('"','')
    nline+=1
    if line.startswith('"'+lookforc):
        print("\ngetting climate for " +lookforc+" from line:")
        print(line)
        q=line.split(',')
        tmxc=[float(x) for x in q[1:13] ]
        print("-"*80)
        print("found the monthly "+lookforc," for "+sitename+":")
        print(tmxc)
        found=True
if not found: print("\nclimate for"+lookforc+" NOT found")
            
    

# %%
daysper=[31,28.25,31,30,31,30,31,31,30,31,30,31]
popc=[round((100*x)/y) for x,y in zip(tmxc,daysper)]
popc

# %% [markdown]
# ## An observation file
# (tip for jupyter notebooks: Shift-O toggles scrolling of long output to cells)

# %%
#First 60 lines of obs:
print(*obs[0:60])

# %% [markdown]
# The ```grep``` process we used for constructing ```obs``` stripped the header lines of the csv files.  So here is the header of an original observation csv file:
# ```
# station_number,area_code,parameter,valid_start,valid_end,value,unit,statistic,instantaneous,level,qc_valid_minutes,qc_valid_minutes_start,qc_valid_minutes_end
# ```
# All time are in [epoch time](https://www.epoch101.com/), in units of seconds. Our python function ```utc```, defined above, does the conversion. Here are some examples of using ```utc```:

# %%
testtime = utc(1430402400)
testtime

# %%
1430431200

# %%
print(testtime)

# %%
for line in obs[0:60]:
    q=line.strip().split(',')
    valid_start=int(q[3])
    valid_end=int(q[4])
    delta=valid_end-valid_start
    print(q[2],"valid_start:", valid_start, utc(valid_start),  "   valid_end:", valid_end, utc(valid_end),delta)

# %% [markdown]
# Note that the forecasted variable ```AIR_TEMP``` is for an instant in time, so ```valid_start=valid_end```.
# For other variables, such as ```AIR_TEMP_MAX```, ```valid_end-valid_start``` is 24 hour period.  The ```qc``` variables are also times, but generally are not of concern in this project.

# %%
print("observations for",sitename)
parl=''
pars={}
for line in obs:
    q=line.split(',')
    par=q[2]
    unit=q[6]
    statistic=q[7]
    instantaneous=q[8]
    if par!=parl:
        if par not in pars:
            pars[par]=[0,unit,statistic,instantaneous]
        parl=par
    pars[par][0]+=1
for par in pars:
    print(par,pars[par])

# %%
lookfor='PRCP'
obsx={}
n=0
j=0
for line in obs:
    q=line.strip().split(',')
    if q[2]!=lookfor:
        continue
    valid_start=int(q[3])
    if valid_start not in obsx:
        obsx[valid_start]=line
        n+=1
    else:
        j+=1
        if line==obsx[valid_start]:
            print(utc(valid_start),valid_start,"duplicate")
        else:
            print(utc(valid_start),valid_start,"different")
            print(line,end='')
            print(obsx[valid_start])
print(sitename,":  ",n," distinct entries for",lookfor)
print(j,"problems with duplicate or different entries for same valid_start time")

# %%
#Here we check for missing data.  Ideally there would be a measurement given 
# every 3600 secs = 1 hr
vs=sorted(obsx.keys())
vl=vs[0]
for v in vs[1:]:
    timegap=v-vl
    if timegap != 3600:
        print("timegap>3600:  ",v, utc(v),"timegap=",timegap)
    vl=v
print(sitename,lookfor)

# %% [markdown]
# ## A forecast file
# The weather forecasts are produced from a [numerical weather predicition](https://en.wikipedia.org/wiki/Numerical_weather_prediction) model (check out the nifty picture of the grid). The forecast model begins from what came out of the previous days results, but with nudging variables, [data assimilation](https://en.wikipedia.org/wiki/Data_assimilation), to conform with the various atmospheric observations that have been recently received. The updated model variables will not exactly conform with the previous pure forecasts for that time, or with the data received. There may be some interest to somebody in what the model was doing in the assimilation period in the past few days, but not us. For most of us, the model results for the future are what we need. Finding some assimilation output in our forecast file can be confusing. See below. 
# 

# %%
#First 4 lines of fcst:
print(*fcsts[0:4])

# %% [markdown]
# The ```grep``` process we used for ```fcst``` stripped the first line, so here it is:
# ```
# station_number,area_code,parameter,valid_start,valid_end,value,unit,statistic,instantaneous,level,base_time
# ```
# We see that the first 4 lines are giving a forecast for Probability of Precipitation, or PoP.
# Let's examine the times in the first 4 lines:

# %%
print(sitename,fcstfile)
print("valid_start                        valid_end                          base_time",end="")
print("                 forecast hour")
for line in fcsts[0:4]:
    q=line.strip().split(',')
    valid_start=int(q[3])
    valid_end=int(q[4])
    base_time=int(q[-1])
    forecasth = (valid_start-base_time)//3600
    print(valid_start,utc(valid_start),"   ",
          valid_end, utc(valid_end),"   ",base_time,utc(base_time),"  ",forecasth )

# %%
print(sitename)
pars={}
for line in fcsts:
    q=line.split(',')
    par=q[2]
    unit=q[6]
    statistic=q[7]
    instantaneous=q[8]
    if par not in pars:
        pars[par]=[0,unit,statistic,instantaneous]
    pars[par][0]+=1
for par in pars:
    print(par,pars[par])

# %% [markdown]
# The ```base_time``` is the model time at which no more data will be added, and the model will be run into the future.  Al the ```base_time``` are apparently 0 UTC, or 10 am AEST.  A few hours [wall-clock time](https://en.wikipedia.org/wiki/Elapsed_real_time) will be needed for the computer program to finish making forecasts for future days.  The model forecast results would be released to the public a few hours after the base-time, which would be afternoon in Australia.  Here is the
# [Time zone information for Melbourne](https://www.timeanddate.com/time/zone/australia/melbourne)
#   Note that there are lines of data with ```valid_start<base_time```.  As explained above, we want to ignore those lines, and analyze genuine forecasts for the future, with the forecast hour positive.  
# 
# Note that ```valid_end-valid_start``` is a 24 hour period for ```DailyPoP```, but it doesn't conform to the boundaries of midnight in Australia.

# %%
utc(1430924400)

# %%
utc(1431010800)

# %% [markdown]
# # find all forecasts for DailyPoP1 or other
# Let's find such forecasts in the file, and put them in a new list ```fcstx```: 

# %%
utc(1430438400)

# %%

lookhour=15 #22,20,10 # 15 for PoP
fcstx=[]
vss={}
vsp={}
for line in fcsts:
    q=line.split(',')
    valid_start=int(q[3])
    valid_end=int(q[4])
    if q[2]==lookforf:
        fcstx.append(line)
        hour=utc(valid_start).hour
        spanh=(valid_end-valid_start)//3600
        vss.setdefault(hour,0)
        vsp.setdefault(spanh,0)
        vss[hour]+=1
        vsp[spanh]+=1
print(sitename)
print("number of line in fcst:",len(fcsts),"   number of lines with "+lookforf,'hour=',lookhour, len(fcstx))
print("start hours",vss)
print("spans",vsp)
if len(vss)!=1 or len(vsp)!=1:
    print(sitename+" may have Daylight savings time issues")

# %%
spanx=24 #  for PoP
starth=15 # Cairns

needset=set([starth+x*24 for x in range(7)])
print(sitename)
vss={}
for line in fcstx:
    q=line.strip().split(",")
    base_time=int(q[-1])
    valid_start=int(q[3])
    valid_end=int(q[4])
    if valid_start not in vss:
        vss[valid_start]=[]
    vss[valid_start].append([valid_end,base_time])
kvs=sorted(vss.keys())
kvl=0
for kv in kvs:
    eba=vss[kv]   
    fha=[(kv-bt)//3600 for ve,bt in eba]
    fha.reverse()
    delta=kv-kvl
    print(kv,delta,len(eba),fha,end='')
    for ve,bt in eba:
        span=(ve-kv)/3600
        if span!= spanx: print("span problem:",kv,ve)
    if kv-3600 in kvs:
        print(" dst problem",end='')
    if starth not in fha:
        print(" gap hours",end='')
    if not needset <= set(fha):
        print(", missing forecast",end='')
    print()
    kvl=kv

# %%
bsts=[]
for line in fcstx:
    q=line.strip().split(",")
    base_time=int(q[-1])
    if base_time not in bsts:
        bsts.append(base_time)
bsts.sort()
btl=bsts[0]
for bt in bsts[1:]:
    timejump=bt-btl
    if timejump>86400:
        print("timejump=",timejump,"seconds,   missing forecasts from",utc(btl+86400))
    btl=bt

# %%
lookforf

# %%
fdict={}
needvr=24 # 15
for line in fcsts:
    q=line.strip().split(",")
    if q[2]!=lookforf: continue
    base_time=int(q[-1])
    bt=utc(base_time)
    if bt.hour !=0 : print("bt=",bt.hour) 
    valid_start=int(q[3])
    valid_end=int(q[4])
    vrange = (valid_end-valid_start)//3600 
    if vrange !=needvr: print(vrange)  
    fhour=(valid_start - base_time)//3600
    par=float(q[5])
    if valid_start not in fdict:
        fdict[valid_start]={}
    if fhour not in fdict[valid_start]:
        fdict[valid_start][fhour]=par
    else:
        print("duplicate")
print(len(fdict))

# %%
kvs = sorted(fdict.keys())
for kv in kvs:
    fhs = sorted(fdict[kv].keys())
    print(kv,utc(kv),fhs)

# %%
testkey=kvs[20] # 20 is arbitrary
print(testkey,utc(testkey))
fdict[testkey]

# %%
obsx[testkey]

# %%
odict={}
spanx=24
for kv in kvs:
    hours = [kv+n*3600 for n in range(spanx)]
    m = 0
    Tsum=0.
    for h in hours:
        if h not in obsx: 
            #print(kv,h,(h-kv)//3600)
            print("missing:",h,"for",kv)
            continue
        else:
            q = obsx[h].strip().split(',')
            val = float(q[5])
            if q[2]!=lookfor: print(q[2])
            Tsum += val
            m += 1
    if m!=spanx:
        print("nope",kv,m)
    else:
        odict[kv] = Tsum
print(len(odict),"found days with ",spanx," hours "+lookfor,"for ",len(kvs),"attempts")

# %%
site

# %%
fdict[testkey]

# %%
edict={} # for export into cvs file
n=0
kvs=sorted(odict)
kvw=kvs[0]
for kv in kvs:
    if kv!=kvw:
        edict[kvw]={'o':'NA'}
    edict[kv]={'o':odict[kv]}
    kvw=kv+86400
print(len(edict))

# %%
for k in sorted(edict):
    print(k, edict[k])

# %%
fdict[testkey]

# %%
for kv in sorted(edict):
    month=utc(kv).month
    edict[kv]['c']=popc[month-1]
    for fn in [1,2,3,4,5,6,7]:
        fh=hour+24*(fn-1)
        if fh in fdict[kv]:
            edict[kv][fn]=fdict[kv][fh]
        else:
            edict[kv][fn]='NA'
            

# %%
for k in sorted(edict):
    print(k, edict[k])

# %%
def z(x):
    f="{: 6.1f} "
    if type(x)==type('a'):
        return '   '+x+'  '
    else:
        return f.format(x)
        

# %%
def zi(x):
    f="{:5d} "
    if type(x)==type('a'):
        return '   '+x+' '
    else:
        return f.format(int(x))
        

# %%
header='   utc         ob   clim   f1    f2    f3    f4    f5    f6    f7'
#print(header)
outfilename=site+'_'+lookforf+outfileext
outfile=open(outfilename,'w')
outfile.write(header+'\n')
for kv in sorted(edict):
    d=edict[kv]
    os=repr(kv)+' '
    os+=z(d['o'])
    os+=zi(d['c'])
    for fn in [1,2,3,4,5,6,7]:
        os+=zi(d[fn])     
#    print(os)
    outfile.write(os+"\n")
outfile.close()                  
print("written:",outfilename)

# %%
with open(outfilename) as testit:
    for line in testit.readlines():
        print(line, end='')


