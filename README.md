# SynetiqDEC
Synetiq Data Engineer Challenge

Initial Upload of challenge py files. Created with IDLE 3.5 and matplotlib for the graph. I hadn't spent much time with python prior to this but thought it'd be a good learning challenge. I made some comments where multithreading or parallel programming might benefit but I did not implement it in this solution mostly because of not being too familiar with Python's capabilities or packages that handled that behavior. 

Download files, run challenge.py, enter the file path for the data files associated with the challenge, and about 80 seconds later you have two csv files output and a scatter chart displaying the instances where stimulus reactions were recorded for at least 15 seconds. X is the RMSSD and y is the average exposure time in seconds. Scale of the dots is the number of times a stimulus instance were hit by a unique user. Labels are for the outlying data points (those that were within 20% of the max value for RMSSD, 20% of the min value for RMSSD, and the top 20% for average seconds exposed). 
