import os
import agent_helper


#Helper for parsing the data
def populate(path, max_output_lines=None):

    last_user_id = 0
    Agents = []
    
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            test_info = None
            user_id = 0
            test_id = 0

            tokens = root.split(os.sep)
            #Use the "data" segment of the path to find the user_id and test_id
            dataToken = (i for i,x in enumerate(tokens) if x == "data")
            for i in dataToken:
                user_id = tokens[i+1]
                test_id = tokens[i+2]
                #Create the test info 
                test_info = agent_helper.AgentTestInfo(test_id, name, os.path.join(root, name))

            Agent = None
            #Make a new agent or use an old one?
            if(user_id == last_user_id):
                #update agent owning user_id
                #only works because walking directory structure
                updateAgentIndex = (i for i,x in enumerate(Agents) if x.user_id == user_id)
                for i in updateAgentIndex:
                    Agents[i].AddTestInfo(test_info)
                    
            else:
                #create new Agent and add AgentTestInfo
                last_user_id = user_id
                Agent = agent_helper.Agent(user_id)
                Agent.AddTestInfo(test_info)
                Agents.append(Agent)
            
   
    return Agents
            
