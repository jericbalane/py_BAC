# BAC Computation Program in Python
# Date created: 19.06.2015
# Author: JERIC BALANE
# Codevil

import utils
import datetime
from math import ceil

app = utils.App()

DENSIT = .8
AMTALC = 15
numOfDrinks = 0
ONEHUN = 100
weight = 0
ONETHOU = 1000
RATIO_MAL = .68
RATIO_FEM = .55
ratio = 0
secondHeader = 0

bac = 0
entered = 0
total = 0
timeLeft = 0
prevtimeLeft = 0

listlog =[]

@app.route('/')
def index():
    global DENSIT,AMTALC,numOfDrinks,ONEHUN,weight,ONETHOU,RATIO_MAL,RATIO_FEM,ratio,bac,entered,total,timeleft,secondHeader,prevtimeLeft,listlog
    
    setVarToOrig()
    
    print """<html><head><link rel="stylesheet" href="/index.css"></head><body>"""
    print '</p>'
    with open('input_file.txt') as f:
        lines = f.read().splitlines()
    # print "INPUT FILE:"
    # for i in range(len(lines)):
        # print '</br>', lines[i]
    # print "</p>"
    
    caseNum = 0
    
    print '<table>'
    
    for i in range(len(lines)):
        
        
        if ' ' in lines[i]:
            # check first if this is a new case
            if 'm' in lines[i] or 'f' in lines [i]:
                print '<tr> <td></td> <td></td> <td></td> <td></td> <td></td> </tr>'
                print '<tr><td>'
                
                setVarToOrig() #reset all data
                caseNum = caseNum + 1
                firstItem, secondItem = lines[i].split()
                print 'case', caseNum, ': ', firstItem, 'kg, ', secondItem # print the first line
                
                print '</td> <td></td> <td></td> <td></td> <td></td> </tr>'
                
                weight = float(firstItem)
                
                # check if its a male or female
                if 'm' in secondItem:
                    ratio = RATIO_MAL
                else:
                    ratio = RATIO_FEM
                
                # print the first header
                print '<tr>\
                       <td> TIME </td>\
                       <td> ENTERED </td>\
                       <td> TOTAL </td>\
                       <td> BAC </td>\
                       <td> TIME LEFT </td>\
                       </tr>'
                
            else:

                firstItem, secondItem = lines[i].split()
                
                total = float(secondItem) + total # compute for the total
                
                if total < 0:   # check if the total is negative integer
                    total = total * -1
                
                timeLeft = (total * 3600) - int(firstItem) # compute for the time left
                
                if timeLeft == 0:
                    timeLeft = float(secondItem) * 3600
                
                bac = (DENSIT * AMTALC * total * ONEHUN) / (weight * ONETHOU * ratio) # compute for the bac
                
                if bac == 0: # check if first instance or not
                    bac = bac
                else:
                    bac = ( bac / (3600 * total) ) * timeLeft
                    
                if prevtimeLeft <= int(firstItem):
                    bac = (DENSIT * AMTALC * float(secondItem) * ONEHUN) / (weight * ONETHOU * ratio) # compute for the bac
                    timeLeft = float(secondItem) * 3600
                
                #assign the items in the table
                print '<tr>'
                print '<td>', firstItem, '</td>'
                print '<td>', secondItem, '</td>'
                print '<td>', total , '</td>'
                print '<td>', str(round(bac,5)).ljust(7, '0') , '</td>'
                print '<td>', str(datetime.timedelta(seconds=int(timeLeft))).rjust(8, '0') ,'</td>'
                print '</tr>'
                
                prevtimeLeft = timeLeft
                
                listlog.append((int(firstItem),total,bac,timeLeft))
                
        else:
        
            if secondHeader == 0:
                secondHeader = secondHeader + 1
                print '<tr>\
                       <td> TIME </td>\
                       <td> BAC </td>\
                       <td> TIME LEFT </td>\
                       <td>  </td>\
                       <td>  </td>\
                       </tr>'
            
            
            # prepare mapping by adding the current timestamp to a list
            listlog.append((int(lines[i]), 0 , 0 , 0 ))
            
            # sort the list for indexing
            listlog.sort()
            
            # start indexing
            index = 0
            for j in listlog:
                if int(lines[i]) == j[0]:
                    # print j[0], 'equals ', int(lines[i])
                    break #break once the index is found
                index = index + 1
            
            # print 'current index is ', index, '; '
            
            del listlog[index] #delete the current index where the temp inserted list is added
            
            
            # main computation for the timestas given
            timeLeft = ( listlog[index-1][0] + listlog[index-1][3] ) - int(lines[i])
            
            if timeLeft <= 0:
                timeLeft = 0
                bac = 0
            else:
                bac = ( listlog[index-1][2] / listlog[index-1][3] ) * timeLeft
            
            
            
            print '<tr><td>', lines[i], '</td>\
                    <td>', str(round(bac,5)).ljust(7, '0') ,'</td>\
                    <td>', str(datetime.timedelta(seconds=int(timeLeft))),' </td>\
                    <td></td>\
                    <td></td>\
                    </tr>'
                    
                    
    print '</table>'
    
    print """</body></html>"""
    
    # printListlog()
    
def printListlog():
    global listlog
    
    print '<pre>',listlog
    
    
def setVarToOrig():
    global DENSIT,AMTALC,numOfDrinks,ONEHUN,weight,ONETHOU,RATIO_MAL,RATIO_FEM,ratio,bac,entered,total,timeleft,secondHeader,prevtimeLeft,listlog
    
    DENSIT = .8
    AMTALC = 15
    numOfDrinks = 0
    ONEHUN = 100
    weight = 0
    ONETHOU = 1000
    RATIO_MAL = .68
    RATIO_FEM = .55
    ratio = 0
    bac = 0
    entered = 0
    total = 0
    timeLeft = 0
    secondHeader = 0
    prevtimeLeft = 0
    listlog = []
    
@app.route('/index.css')
def css():
    print """
    body {
        font-family: verdana, sans serif;
        line-height: 1.3;
        font-size: 83%;
    }
    
    table, tr, td {
        border: 1px solid black;
    }
    
    """
    
if __name__ == "__main__":
    print "Run the file run.py instead."
    raw_input()