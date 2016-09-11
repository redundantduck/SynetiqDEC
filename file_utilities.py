from datetime import timezone
from datetime import datetime 
import datetime 
import csv
import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


try:
    input = raw_input
except NameError:
    pass

def prompt(message, errormessage, isvalid, default):
    """Prompt for input given a message and return that value after verifying the input.

    Keyword arguments:
    message -- the message to display when asking the user for the value
    errormessage -- the message to display when the value fails validation
    isvalid -- a function that returns True if the value given by the user is valid

    Credit to http://stackoverflow.com/users/940217/kyle-falconer
    """
    res = None
    while res is None:
        res = input(str(message)+': ')
        if(len(res) == 0):
            res = default
        if not isvalid(res):
            print(str(errormessage))
            res = None
    return res

#stimulus_tuple: used for collecting the stimulus_id, start and end times, and if this instance qualifies for the 15 second threshold
class stimulus_tuple:

    limit = datetime.time(0,0,15)
    
    def __init__(self, datetime_start, datetime_end, id):
        try:
            self.datetime_start = datetime.datetime.strptime(datetime_start[:-6], "%Y-%m-%d %H:%M:%S.%f")
        except:
            self.datetime_start = datetime.datetime.strptime(datetime_start[:-6], "%Y-%m-%d %H:%M:%S")
          
        try:
            self.datetime_end = datetime.datetime.strptime(datetime_end[:-6], "%Y-%m-%d %H:%M:%S.%f")
        except:
            self.datetime_end = datetime.datetime.strptime(datetime_end[:-6], "%Y-%m-%d %H:%M:%S")
            
        self.id = id
        self.time_difference = self.datetime_end - self.datetime_start
        if self.time_difference.total_seconds() >= stimulus_tuple.limit.second:
            self.threshold_hit = True
        else:
            self.threshold_hit = False
            
#simple class for collecting information on the datetime and the value
class hr_tuple:

    def __init__(self, datetime, value):
        self.datetime = datetime
        self.value = float(value)

#class to parse data and translate start and end times of a stimulus reading   
class loader_stimulus_file:

    def __init__(self, path):
        
        last_id = ""
        start = ""
        end = ""
        self.stimulus_list = []
        try:
            file = open(path)
            reader = csv.reader(file)
            
        
            for row in reader:
                if row[0] != "server_time":

                    if row[1] == last_id+"_end":
                        end = row[0]
                        s = stimulus_tuple(start, end, last_id)
                        self.stimulus_list.append(s)
                
                        last_id = row[1]
                    else:
                        last_id = row[1]
                        start = row[0]
             
        finally:
            file.close()
       
        #print(len(stimulus_list))

#class for parsing the hr file and transforming the unix_utc timestamp into a standard datetime for easier translation
class loader_hr_file:

    def __init__(self, path):
        file = open(path)
        reader = csv.reader(file)

        self.hrs = []
        
        for row in reader:
            if row[0] != "unix_utc":
                h = hr_tuple(datetime.datetime.strptime(datetime.datetime.utcfromtimestamp(int(row[0][:-2])).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S'), row[2])
                self.hrs.append(h)

#class for writing the output csvs with only one point of inspection on the customClass variable for creating the aggregate file
class write_output_csv:

    def __init__(self, dataArray, fileName, customClass):
        with open(fileName,'w',newline='') as csv_output:
            dataWriter = csv.writer(csv_output)
            if(customClass == True):
                dataWriter.writerow(['Stimulus_id','AvgRMSSD'])
                for item in dataArray:
                    dataWriter.writerow([item.stimulus_id,item.getAverage()])
            else:
                for row in dataArray:
                    dataWriter.writerow(row)
#graphing class which is admittedly messy as I figured out how to use pylab
class write_output_plot:

    def __init__(self, xDataArray, yDataArray, zDataArray, wDataArray, xLabel, yLabel, title):

        objects = xDataArray
        minTick = int(min(yDataArray))
        maxTick = int(max(yDataArray))
        minTickX = int(min(wDataArray))
        maxTickX = int(max(wDataArray))
        
        y_pos = np.arange(start=minTick, stop=maxTick)
        x_pos = np.arange(start=minTickX, stop=maxTickX)

        labels = xDataArray
        plt.scatter(yDataArray,wDataArray, marker= 'o', s=zDataArray, label=xDataArray, c=yDataArray)
        for label, x, y in zip(labels, yDataArray, wDataArray):
            if(x >= (maxTick*0.80) or x <= (minTick*1.20) or y >= (maxTickX*0.80)):
                plt.annotate(
                    label, 
                    xy = (x, y), xytext = (-20, 20),
                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                    bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

        plt.ylabel(yLabel)
        plt.xlabel(xLabel)
        plt.title(title)
 
        plt.show()
        
        

