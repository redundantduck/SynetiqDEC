import agent_populator
import agent_helper
import file_utilities
import sys
import operator
import os
import datetime

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

filepath = file_utilities.prompt(
        message = "Enter the file path to the base [data] directory. Blank value defaults to C:\join_us-master\data_engineer\data", 
        errormessage= "The file path you provided does not exist",
        isvalid = lambda v : os.path.isdir(v),
        default = "C:\join_us-master\data_engineer\data")
print(datetime.datetime.now().time())
print("Processing files...")
#begin collecting data about the files from local copy
Agents = agent_populator.populate(filepath)
CleanedAgents = []
#Iterate through the Agents list, validate file couplings, and create a list of valid agents
#This could be run multi-threaded or in parallel

for a in Agents:
    a.ValidateFileCoupling()
    if a.valid:
        CleanedAgents.append(a)

#Clear Agents list because it's no longer needed
Agents = None
print("Number of cleaned agents {}".format(str(len(CleanedAgents))))
#This could be run multi-threaded or in parallel
print("Processing user/stimulus couplings")

for ca in CleanedAgents:
    ca.ProcessCouplings()
    ca.CalculateRMSSD()
    #print("Agent {}; Avg RMSSD {}".format(ca.user_id, ca.AverageRMSSD))

#print(sorted(agent_helper.ProcessedTestInfo.Stimulus_id_list))
print("Number of stimulus ids {}".format(len(agent_helper.ProcessedTestInfo.Stimulus_id_list)))
print("Cleaning data")

xMax = len(agent_helper.ProcessedTestInfo.Stimulus_id_list) + 1
yMax = len(CleanedAgents) + 1

aggregateStims = []

Matrix = [[0 for row in range(0,yMax)] for col in range(0,xMax)]
Matrix[0][0]="StimulusID/UserID"
yIndex = 0
xIndex = 1

for i in agent_helper.ProcessedTestInfo.Stimulus_id_list:
   # print(xIndex)
    Matrix[xIndex][yIndex] = i

    xIndex += 1
    
   # yIndex += 1

yIndex = 1
xIndex = 0

print("Preparing data for output")
#This could be run multi-threaded or in parallel but care would be needed to ensure safety of aggregateStims list
for i in CleanedAgents:

    Matrix[xIndex][yIndex] = i.user_id
    for t in i.ProcessedTestInfo:
        try:
            stimulusIndex = (sid for sid,x in enumerate(agent_helper.ProcessedTestInfo.Stimulus_id_list) if x == t.getKey())
            for s in stimulusIndex:
                    Matrix[s+1][yIndex] = t.rmssd
                    if(t.threshold_hit == True):
                        
                        try:
                            stim_id = Matrix[s+1][0]
                           # print("threshold hit; stimID = {}".format(stim_id))
                        
                            if contains(aggregateStims, lambda x: x.stimulus_id == stim_id):
                                for aggItem in aggregateStims:
                                    if aggItem.stimulus_id == stim_id:
                                       aggItem.addValue(t.rmssd)
                                       aggItem.addSeconds(t.getSecondsRunning())
                                       break
                                
                        #find index ID and add value
                            else:
                        #create new AggregateTestInfo and add to list
                                aggInfo = agent_helper.AggregateTestInfo((stim_id))
                                aggInfo.addValue(t.rmssd)
                                aggInfo.addSeconds(t.getSecondsRunning())
                                aggregateStims.append(aggInfo)
                        except Exception as inst:
                             print("Error with {}", inst)

        except:
            print("Error with {}".format(t))
        #    print(t.agent_id)
        #    print(t.rmssd)
    yIndex += 1

    ##Matrix[0][yIndex] = the userIDs
    ##Matrix[xIndex][0] = the stimulus IDs
    ##when populating the userIDs, then check for a stimulus ID score, if found, place value

    
sortedAggs = sorted(aggregateStims, key=operator.attrgetter('stimulus_id'))
#StimulusIDs
plotXArray = []
#Average RMSSD
plotYArray = []
#Number of Instances
plotZArray = []
#Average Seconds
plotWArray = []

#This could be run multi-threaded or in parallel
for item in sortedAggs:
    plotXArray.append(item.stimulus_id)
    plotYArray.append(item.getAverage())
    plotZArray.append(item.count)
    plotWArray.append(item.getAverageSeconds())
                      
#    print(item)

try:
    print("Create file {}{}{}".format(filepath,os.sep,"FullOutput.csv"))
    file_utilities.write_output_csv(Matrix, "FullOutput.csv", False)
except Exception as inst:
    print("Error with {}", inst)
try:
    print("Create file {}{}{}".format(filepath,os.sep,"Averaged.csv"))
    file_utilities.write_output_csv(sortedAggs, "Averaged.csv", True)
except Exception as inst:
    print("Error with {}", inst)
print(datetime.datetime.now().time())
try:
    print("Create plot {}".format("Avg RMSSD for Stimulus Instances Greater than 15 Seconds"))
    file_utilities.write_output_plot(plotXArray, plotYArray, plotZArray, plotWArray, "Avg RMSSD","Avg Seconds Active","Avg RMSSD for Stimulus Instances Greater than 15 Seconds")
except Exception as inst:
    print("Error with {}", inst)

print("Program execution complete")
                                                            




