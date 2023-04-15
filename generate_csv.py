import csv 
    
# field names 
fields = ['Episode', 'Timestamp', 'Position_Shan', 'Position_Thigh', 'Velocity_Shank', 'Velocity_Thigh','Torque_Shank', 'Torque_Thigh','Force'] 
    

    
# name of csv file 
filename = "Dataset_15_04.csv"
    
# writing to csv file 
with open(filename, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(fields) 
