import math
import file_utilities

#Initial class for collecting test id and file location data
class AgentTestInfo:

    def __init__(self, test_id, file_type, file_path):
        self.test_id = test_id
        self.file_type = file_type
        self.file_path = file_path

#AggregateTestInfo is used when compiling results from ProcessedTestInfo 
class AggregateTestInfo:
    def __init__(self, stimulus_id):
        self.stimulus_id = stimulus_id
        self.value = 0
        self.count = 0
        self.seconds = 0

    def addValue(self, value):
        self.value = self.value + value
        self.count = self.count + 1

    def addSeconds(self, seconds):
        self.seconds = self.seconds + seconds
        

    def getAverage(self):
        returnValue = 0
        if(self.value > 0 and self.count >0):
            returnValue = (self.value / self.count )
        return returnValue
    def getAverageSeconds(self):
        returnValue = 0
        if(self.seconds > 0 and self.count > 0):
            returnValue = (self.seconds / self.count )
        return returnValue
    
    def getKey(self):
        return self.stimulus_id
    
    def __repr__(self):
        return "stimulus_id: {}  | value: {} | count: {} | avg: {} | secondsactive {}".format(self.stimulus_id, self.value, self.count, self.getAverage(), self.getAverageSeconds())

    def __cmp__(self, other):
        if hasattr(other, "getKey"):
            return self.getKey().__cmp__(other.getKey())

#ProcessedTestInfo is the primary info class that contains information about the agent, stimulus, and the coupled instances
# of agent/user_id processing a given stimulus
class ProcessedTestInfo:


    Stimulus_id_list = []
    
    def __init__(self,  stimulus_id,  agent_id, stimulus_time_start, stimulus_time_end, threshold_hit, rr_list):

        if stimulus_id not in ProcessedTestInfo.Stimulus_id_list:
            ProcessedTestInfo.Stimulus_id_list.append(stimulus_id)
            #print("Adding {}".format(stimulus_id))
         
        self.stimulus_id = stimulus_id
        
        self.agent_id = agent_id
        self.stimulus_time_start = stimulus_time_start
        self.stimulus_time_end = stimulus_time_end
        self.rr_list = rr_list
        #print(len(self.rr_list))
        self.rr_intervals = 0
        self.threshold_hit = threshold_hit
    
        self.rmssd = self.calculateRMSSD()
        
        
    def __repr__(self):
        return "{}".format(self.stimulus_id)

    def __cmp__(self, other):
        if hasattr(other, "getKey"):
            return self.getKey().__cmp__(other.getKey())

    def getKey(self):
        return self.stimulus_id

        
    def calculateRMSSD(self):
    
        intervals = []
        if(len(self.rr_list) > 0):
            workingValue = self.rr_list[0].value
            
        for i in range(len(self.rr_list)-1):
           # print(math.fabs(self.rr_list[i].value - self.rr_list[i+1].value)**2)
            if(self.rr_list[i+1].value < (workingValue * 1.5)):
                intervals.append( math.fabs(self.rr_list[i].value - self.rr_list[i+1].value)**2 )
                workingValue = self.rr_list[i].value
            #else:   
                #do nothing for now
                #intervals.append( math.fabs(self.rr_list[i].value - self.rr_list[i+1].value)**2 )
            #print(intervals)
        try:
            #print("sum {}; length {};".format(sum(intervals),len(intervals)))
            average = sum(intervals)/len(intervals)
        except:
            average = 0
        sqrt = math.sqrt(average)

        return sqrt

    def getSecondsRunning(self):
        timeRunning = self.stimulus_time_end - self.stimulus_time_start
        return timeRunning.total_seconds()
        
    
#Agent is a class for the user_id instance. It contains information about what stimulus_ids were processed, the user
#instrument readings, and if the user is valid based on if they have at least one stimulus_id and one instrumentation file coupled
class Agent:

    def __init__(self, user_id):
        self.user_id = user_id
        self.valid = False
        self.couplings = []
        self.AgentTestInfoCollection = []
        self.ProcessedTestInfo = []
        self.AverageRMSSD = 0

    def AddTestInfo(self, AgentTestInfo):
        self.AgentTestInfoCollection.append(AgentTestInfo)

    def ValidateFileCoupling(self):
        stimuli = (i for i,x in enumerate(self.AgentTestInfoCollection) if x.file_type == "stimulus.csv")
        for i in stimuli:
            hrs = (h for h,x in enumerate(self.AgentTestInfoCollection) if x.file_type == "hr_gsr.csv" and x.test_id == self.AgentTestInfoCollection[i].test_id)
            for h in hrs:
                self.couplings = self.couplings + [i,h]
        if len(self.couplings) > 0:
            self.valid = True
            
    def ProcessCouplings(self):
        #couplings are in Stimulus | HR tuples
        #print("Couplings {}".format(self.couplings[0]))
        stimuli = self.ProcessStimulusFile(self.couplings[0])
        rr = self.ProcessHRFile(self.couplings[1])

     
        rrlist = []
        for s in stimuli.stimulus_list:
            #rrs = (r for r,x in enumerate(rr.hrs) if x.datetime >= s.datetime_start and x.datetime <= s.datetime_end)
            for r in rr.hrs:
                #print("r datetime {}; s start {}; s end {};".format(r.datetime,s.datetime_start, s.datetime_end))
                if r.datetime >= s.datetime_start and r.datetime <= s.datetime_end:
                    rrlist.append(r)
                
            processedStimuli = ProcessedTestInfo(s.id, self.user_id, s.datetime_start, s.datetime_end, s.threshold_hit, rrlist)
            
            self.ProcessedTestInfo.append(processedStimuli)
       
    def ProcessStimulusFile(self, index):
        
        stimuli = file_utilities.loader_stimulus_file(self.AgentTestInfoCollection[index].file_path)
        return stimuli
            
    def ProcessHRFile(self, index):
        hr = file_utilities.loader_hr_file(self.AgentTestInfoCollection[index].file_path)
        return hr;
    
    def CalculateRMSSD(self):
        count = 0
        runningTotal = 0;
        for i in self.ProcessedTestInfo:
            if(i.threshold_hit == True):
                count += 1
                runningTotal += i.rmssd
        if(count > 0):
            self.AverageRMSSD = runningTotal / count

 
            
        
        
