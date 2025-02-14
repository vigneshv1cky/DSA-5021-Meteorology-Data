##############################################
#
##############################################

import os
from urllib.request import urlopen
import copy
import matplotlib.pyplot as plt
from datetime import datetime as dt

utc = dt.utcfromtimestamp

##############################################
#
##############################################

from IPython.core.display import display, HTML

# Define the CSS styles
custom_styles = """
<style>
    div.text_cell_render {
        background-color: #ded; 
        font-size: 18px;
    }
    .rendered_html code {
        background-color: #ded; 
        color: #900; 
        font-size: 16px;
    }
    .rendered_html pre {
        background-color: #ded; 
        color: #900; 
        font-size: 16px;
    }
</style>
"""

# Apply the styles
display(HTML(custom_styles))

##############################################
#
##############################################


# for automatically downloading data files from http://dsa5021.net/data/, or other url
def grabfile(urlfront, filename, filedir=""):  # filedir could be data/, for example"
    urlpath = urlfront + filename
    filepath = filedir + filename
    if os.path.exists(filepath):
        print(filepath, " already exists.  Delete it, if you want to overwrite.")
        return
    with urlopen(urlpath) as response:
        body = response.read()
    with open(filepath, "wb") as f:
        f.write(body)
    print("downloaded " + urlpath + " to " + filepath)
    return


##############################################
#
##############################################

yourname = (
    "Vignesh Murugan"  # this label is put on your figures, your name is NOT metrprof
)

##############################################
#
##############################################

# I have made 6 CSV files for you from the Australian data.
filenames = """
31011_AIR_TEMP_MAX.csv
12038_AIR_TEMP_MAX.csv
09021_AIR_TEMP_MAX.csv
31011_AIR_TEMP_MIN.csv
12038_AIR_TEMP_MIN.csv
09021_AIR_TEMP_MIN.csv
""".strip().split()

usefile = 2  # you choose a file here

infilename = filenames[usefile]
print("you chose:", infilename)

##############################################
#
##############################################

# download the data file, if needed
if not os.path.exists(infilename):
    grabfile("http://dsa5021.net/data/", infilename)
else:
    print("you already have " + infilename)

##############################################
#
##############################################

# the filename contains information about the file you chose
sitenum = infilename.split("_")[0]  # grabs sitenum from the filename you chose
siteinfo = {
    "31011": "CAIRNS AERO",
    "12038": "KALGOORLIE-BOULDER AIRPORT",
    "09021": "PERTH AIRPORT",
}
sitename = siteinfo[sitenum]
varname = infilename[len(sitenum) + 1 : -4]
print("this is what you are studying:")
print(sitenum)
print(sitename)
print(varname)

##############################################
#
##############################################

# read and inspect the chosen data file
lines = open(infilename).readlines()
for line in lines:
    print(line, end="")
# use shift-O to scroll this output:

##############################################
#
##############################################

testtime = utc(1430431200)
testtime

testtime.month

print(testtime)


colnames = lines[0].strip().split()
print(colnames)
fkeys = colnames[3:]
print(fkeys)  # forecast lead times, f1= 1 day, f2= 2 day ...


##############################################
# This script processes a dataset, creating a nested dictionary
# (edictf) to store observations, climate, and forecast data
# using UTC timestamps as keys.
##############################################

edictf = {}
for line in lines[1:]:
    components = line.strip().split()
    timeob = int(components[0])
    edictf[timeob] = {}

    for i, colname in enumerate(colnames[1:], start=1):
        value = components[i]
        edictf[timeob][colname] = float(value) if value != "NA" else value

ekeys = sorted(edictf.keys())
print(f"edictf has {len(ekeys)} keys")


testkey = ekeys[100]
print(testkey)
print(utc(testkey))  # utc converts epoch time to UTC time
print(edictf[testkey])


# Look at edictf
for k in ekeys[:10]:
    print(k)
    print(edictf[k])

"""

# hack!

[What does Hack Mean?](https://www.techopedia.com/definition/27859/hack-development) I like that answer. I will cut and paste it here:

*Hack, in the context of development, has two meanings:*

1.  *A hack is an inelegant solution to a problem. In this sense, a hack gets the job done but in an inefficient, un-optimal or ugly way.*
1. *To hack can also mean to program with exceptional skill. In this sense, a hacker produces code that not only accomplishes the task, but does so in an efficient and unique manner.*

To assess the skill of  persistence forecasts, I hacked this notebook to allow substituting model forecast predictions with persistence forecast predictions.  Is this efficient or ugly? 

Don't set `hack=True` until you are instructed to do so later in the notebook.

"""

hack = (
    False  # True will use substitute persistence forecasts instead of model forecasts
)

edictp = copy.deepcopy(edictf)  # ready to hack the forecast data
for k in ekeys:
    for f in fkeys:
        n = int(f[1])
        priortime = k - n * 86400  # for extracting prior ob
        priorob = "NA"  # default is "Not Available"
        if priortime in edictp:  # prior ob exists
            priorob = edictp[priortime]["ob"]  # get prior ob
        edictp[k][f] = priorob  # replace model forecast with prior ob


if hack:
    edict = edictp  # point edict to hacked persistence forecast dictionary
    forecast = "persistence"
else:
    edict = edictf  # point edict to original model forecast dictionary
    forecast = "model"
print("you are using:", forecast, "forecasts")


"""
Let's assess the error in the forecasts, meaning the numerical difference between the forecast and the observation. 
We are interested in the average error over all the forecasts. We calculate *Root Mean Square Error* `RMSE` and *Mean Absolute Error* `MAE`. 
[RMSE and MAE](http://www.eumetrain.org/data/4/451/english/msg/ver_cont_var/uos3/uos3_ko1.htm)

In order to do arithmetic, we will reject all days that had missing values (NA) in `ob` or `clim`  or `f1` or `f2` ... 

Note that `f7` is not necessarily needed in a study of `f1`.  But we choose to do the forecast comparisons on the same set of events. All forecasts must be available.

There is a surprising amount of missing data.  I am not sure why.
"""

gkeys = []  # gkeys are "good" keys
for k in ekeys:
    if "NA" in edict[k].values():
        continue  # one or more NA, throw out key
    gkeys.append(k)
print(
    "number of keys =",
    len(ekeys),
    "    number of keys with no missing values",
    len(gkeys),
)


# extracts values from a list of lists
# kk is the subset of keys of adict that you want to include
# ka = ob, clim, or f1, ... , the key of the inner list
# the values for ka are put sequentially into a list
def getv(adict, kk, ka):
    w = []  # empty list
    for k in kk:
        w.append(adict[k][ka])  # fill the list
    return w


# makes the lists oo, cc, ffs['f1'] ... will be used in plotting and assessment of skill
ffs = {}
oo = getv(edict, gkeys, "ob")  # all the ob
cc = getv(edict, gkeys, "clim")  # all the clim
tdays = [(x - gkeys[0]) / 86400 for x in gkeys]  # elapsed days
for fk in fkeys:
    ffs[fk] = getv(edict, gkeys, fk)  # all the f1, f2, ...


"""

We have observations in list `oo`, expectation from past climate data in `cc`, day number in `tdays`, 
and seven forecasts, from one day prior, two days prior... in `f1`, `f2` and so on...

Make a quick plot. Compare obs, climate and a forecast.
It shold be obvious that f1 (the 1-day forecast, the forecast for tomorrow)
is better than using climatology as a forecast.

"""

plt.figure(figsize=(18, 3))
plt.plot(tdays, oo, "g.", label="obs")  # green dot for ob
plt.plot(tdays, cc, "r.", label="climate")  # red dot for climatology
plt.plot(tdays, ffs["f1"], "m.", label="f1")  # magenta dot for forecast
plt.title("forecast type: " + forecast)
plt.legend()  # <- notice last semi-colon to supress messages


# assess numerical difference between two lists
def meane(a, b):
    assert len(a) == len(b)
    sumsq = 0  # sum of square difference
    suma = 0  # sum of absolute difference
    z = zip(a, b)
    for x, y in z:
        sumsq += (x - y) ** 2
        suma += abs(x - y)
    n = len(a)
    # return both 'root mean square error' and 'mean absolute error'
    return (sumsq / n) ** 0.5, suma / n


# find the error for using climate to predict observation
rmsec, maec = meane(oo, cc)
print("RMSE climate = ", rmsec, "     MAE climate = ", maec)


# find the error for using f1 to predict observation
rmsef1, maef1 = meane(oo, ffs["f1"])
print("RMSE one-day forecast = ", rmsef1, "     MAE one-day forecast = ", maef1)


skills = []  # for RMSE skill
skilla = []  # for MAE skill
skilld = {"clim": 0.0}  # will be useful for plots
print("forecast type:", forecast)
print("using    RMSE climate = {:6.3}     MAE climate =  {:6.3}\n".format(rmsec, maec))
print("forecast    RMSE    Skill    MAE    Skill")
for fk in fkeys:
    ff = ffs[fk]
    rmsef, maef = meane(oo, ff)
    sks = 1.0 - rmsef / rmsec
    ska = 1.0 - maef / maec
    outform = "{}        {:6.3}  {:6.3}  {:6.3}  {:6.3}"
    outstring = outform.format(fk, rmsef, sks, maef, ska)
    print(outstring)
    skills.append(sks)  # skill using RMSE, for bar graph
    skilla.append(ska)  # skill using MAE, for bar graph
    skilld[fk] = sks  # RMSE skill in this dictionary, for scatter plot labels


plt.figure(figsize=(8, 4))
plt.title(varname + ",  " + forecast + " RMSE Skill Score,  " + sitename)
color = "blue"
if hack:
    color = "red"
plt.bar(fkeys, skills, color=color)  # note skills
plt.text(0.0, 0.0, yourname, fontsize=48, alpha=0.1)
plt.savefig("skillscoresRMSE" + forecast + ".png")


plt.figure(figsize=(8, 4))
plt.title(varname + ",  " + forecast + " MAE Skill Score,  " + sitename)
plt.bar(fkeys, skilla, color=color)  # note skilla
plt.text(0.0, 0.0, yourname, fontsize=48, alpha=0.1)
plt.savefig("skillscoresMAE" + forecast + ".png")


# this format will be useful for some of the plots below
skt = "skill score={: .2f}"
skt.format(skilld["f1"])


fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(13, 4), facecolor="yellow")
if "MAX" in varname:
    tlo = 10
    thi = 45
else:
    tlo = -5
    thi = 30
fsz = 18
tcks = range(tlo, thi + 1, 5)

color = "blue"
if hack:
    color = "red"

skt = "skill score= {: .2f}"

title = skt.format(skilld["f1"])
ax[0].set_xlim(tlo, thi)
ax[0].set_ylim(tlo, thi)
ax[0].plot(ffs["f1"], oo, ".", color=color)
ax[0].set_xlabel("f1", fontsize=fsz)
ax[0].set_ylabel("ob", fontsize=fsz)
ax[0].set_xticks(tcks)
ax[0].set_yticks(tcks)
ax[0].set_title(title)
ax[0].set_aspect("equal")

title = skt.format(skilld["f7"])
ax[1].set_xlim(tlo, thi)
ax[1].set_ylim(tlo, thi)
ax[1].plot(ffs["f7"], oo, ".", color=color)
ax[1].set_xlabel("f7", fontsize=fsz)
ax[1].set_xticks(tcks)
ax[1].set_yticks(tcks)
ax[1].set_title(title)
ax[1].set_aspect("equal")

title = skt.format(skilld["clim"])
ax[2].set_xlim(tlo, thi)
ax[2].set_ylim(tlo, thi)
ax[2].plot(cc, oo, ".", color=color)
ax[2].set_xlabel("clim", fontsize=fsz)
ax[2].set_xticks(tcks)
ax[2].set_yticks(tcks)
ax[2].set_title(title)
ax[2].set_aspect("equal")

figtitle = varname + "  " + "forecast=" + forecast + "   " + sitename
fig.text(0.5, 1, figtitle, ha="center", fontsize=fsz)
fig.text(0.1, 0.5, yourname, fontsize=48, alpha=0.1)
fig.text(0.90, 0.95, "n=" + repr(len(oo)))
outpng = infilename[:-4] + "_" + "scatter" + "_" + forecast
fig.savefig(outpng + ".png", bbox_inches="tight", facecolor="yellow", transparent=False)


def fplot(tdays, oo, ff, lab, title):
    rmse, mae = meane(oo, ff)
    rootmeansq = "{:.3f}".format(rmse)
    quick, simple = plt.subplots(figsize=(18, 3))
    simple.plot(tdays, oo, ".g", lw=1, ms=3, zorder=1)
    for i in range(0, len(tdays)):
        if oo[i] > ff[i]:
            segcol = "r"
        else:
            segcol = "b"
        simple.plot(
            (tdays[i], tdays[i]), (ff[i], oo[i]), segcol, linewidth="1.", zorder=0
        )
    simple.set_xticks(range(0, 360, 30))  # x tick marks every 30
    simple.set_ylabel("degree C")
    simple.set_xlabel("day")
    simple.set_title(title, fontsize=22)
    # bb    simple.text(.1,.2,'your name here!',fontsize=72, alpha=.1, transform = simple.transAxes)
    simple.text(0.05, 0.8, "RMSE=" + rootmeansq, transform=simple.transAxes)
    quick.savefig(lab + ".png", dpi=144)


for thef in fkeys:
    outpng = infilename[:-4] + "_" + thef + "_" + forecast
    title = varname + "  ob vs. " + thef + "  " + forecast + "  " + sitename
    print(title, ffs[thef][:10])
    fplot(tdays, oo, ffs[thef], outpng, title)

title = varname + "  ob vs. climate  " + sitename
print(title, cc[:10])
outpng = infilename[:-4] + "_clim"
fplot(tdays, oo, cc, outpng, title)


"""

STUDENT EXERCISES

## using the dictionary
Here is what should a simple exercise to make sure you understand our `edictf`, which has dictionaries within the dictionary.  For file `09021_AIR_TEMP_MAX.csv`, how many `NA` are within are in `f1`, `f2` ... `f7`?
Give your answer as a list of 7 integers.  Hint: `nas[-1]` is 32.

"""

# STUDENTS: how many "NA"
nas = [0, 0, 0, 0, 0, 0, 0]
for k in edictf.keys():
    for m in range(7):
        forecast_key = f"f{m + 1}"  # Construct the forecast key (f1, f2, ..., f7)
        if edictf[k][forecast_key] == "NA":  # Check if the value is "NA"
            nas[m] += (
                1  # Increment the respective counter1  # Increment the corresponding NA count if the value is "NA"
            )

print(infilename)
print("forecast type:", forecast)
print(nas)
# nas item will not be only 0
# your answer will be submitted in the quiz

"""
09021_AIR_TEMP_MAX.csv
forecast type: persistence
[25, 26, 27, 28, 29, 29, 32]

"""

##############################################
#
##############################################

# STUDENTS, calculate TP FP FN TN
fn = "f1"  # choose the forecast, f1, f2, ...f7.
ff = ffs[fn]
TP = 0
FP = 0
FN = 0
TN = 0
dt = 5  # you choose temperature increment above climatological forecast
for f, o, c in zip(ff, oo, cc):
    print("f=", f, "  o=", o, "  c=", c)  # delete this after you understand
    if f > (c + dt):
        if o > (c + dt):
            TP += 1
        else:
            FP += 1
    else:
        if o > (c + dt):
            FN += 1
        else:
            TN += 1


print(infilename)
print("weather event: temperature", dt, "C above climatology")
print("forecast type:", forecast, fn)
print("TP=", TP, "   FP=", FP)
print("FN=", FN, "   TN=", TN)


"""
09021_AIR_TEMP_MAX.csv
weather event: temperature 5 C above climatology
forecast type: model f1
TP= 32    FP= 4"""
