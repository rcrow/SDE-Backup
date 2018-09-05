import arcpy
import datetime
import pandas #Tested with version 0.19.1
import smtplib

def sendEmail(fromaddr,toaddrs,msg):
    print("Sending an email")
    params = pandas.read_excel("backupParameters.xlsx", sheetname='email')
    print(params)
    username=params.iat[0,0]
    password=params.iat[0,1]
    print(username)
    print(password)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

connectionPath = arcpy.env.scratchFolder

# Create string from date and time
time = datetime.datetime.now()  # Get system time
if len(str(time.month)) == 1:
    month = "0" + str(time.month)
else:
    month = str(time.month)
if len(str(time.day)) == 1:
    day = "0" + str(time.day)
else:
    day = str(time.day)
if len(str(time.hour)) == 1:
    hour = "0" + str(time.hour)
else:
    hour = str(time.hour)
if len(str(time.minute)) == 1:
    minute = "0" + str(time.minute)
else:
    minute = str(time.minute)
if len(str(time.second)) == 1:
    second = "0" + str(time.second)
else:
    second = str(time.second)

def checkAndDelete(CDpath):
    if arcpy.Exists(CDpath):
        print(CDpath +": Exists, Deleted")
        arcpy.Delete_management(CDpath)
    else:
        print(CDpath +": Does Not Exist")

params = pandas.read_excel("backupParameters.xlsx")
servers=params['SDE_server'].tolist()
dbs=params['SDE_db'].tolist()
prefix=params['Export_prefix'].tolist()
suffix=params['Export_suffix'].tolist()
filenames=[]
for index, file in enumerate(prefix):
    filenames.append(prefix[index] + str(time.year) + month + day + "_" + hour + minute + second + suffix[index])
exportPaths=params['Export_path'].tolist()

for i in range(0,len(servers)):
    print("Server: "+servers[i])
    print("Database: " + dbs[i])
    arcpy.env.overwriteOutput = True
    #Get a lock error message when I try this - not necissarily needed but might be a good double check to implement at some point
    #checkAndDelete(connectionPath + "\\" + "ConnectForBackupTo_"+servers[i] + dbs[i]+".sde") #Just to make sure it deletes any connection with the exact same name in the destination
    arcpy.CreateDatabaseConnection_management(connectionPath, "ConnectForBackupTo_"+servers[i] +"_"+ dbs[i], "POSTGRESQL", servers[i], "OPERATING_SYSTEM_AUTH", "#", "#", "#", dbs[i])
    arcpy.env.overwriteOutput = False

    arcpy.env.workspace = connectionPath + "\\" + "ConnectForBackupTo_"+servers[i] +"_"+ dbs[i]+".sde"

    print("Connection: " + str(arcpy.env.workspace))

    filename = filenames[i]

    # Create the file geodatabase
    path = exportPaths[i]
    arcpy.CreateFileGDB_management(out_folder_path=path,
                                   out_name=filename,
                                   out_version="CURRENT")

    # Path and file name of new geodatabase
    gdOutput = path + "\\" + filename + ".gdb"
    print("Export destination: " + gdOutput)  # print for fun :)

    #List feature in SDE
    datasetList = arcpy.ListDatasets('*','Feature')

    #Cycle through all the feature datasets (Not sure what it would do if a feature class was loose in there??)
    for dataset in datasetList:
        datasetPath = arcpy.env.workspace+"\\"+dataset #Get the full path
        simpName=dataset.split(".")[-1] #Cut off anything before the last period
        #Copy the feature class
        arcpy.Copy_management(in_data=datasetPath,
                              out_data=gdOutput + "\\"+simpName)
        print("Finished copying: " + dataset)

    # List Tables in SDE
    tableList = arcpy.ListTables('*', 'ALL')

    # Cycle through all the tables
    for table in tableList:
        tablePath = arcpy.env.workspace + "\\" + table  # Get the full path
        simpName = table.split(".")[-1]  # Cut off anything before the last period
        # Copy the feature class
        arcpy.Copy_management(in_data=tablePath,
                              out_data=gdOutput + "\\" + simpName)
        print("Finished copying: " + table)

#Email addresses for use in sending emails
fromaddr = pandas.read_excel("backupParameters.xlsx", sheetname='email').iat[0,0] #get email address from param file
toErrorAddrs = pandas.read_excel("backupParameters.xlsx", sheetname='email').iat[0,0]
toaddrs = ['crow.ryan@gmail.com','tfelger@usgs.gov']

msg = "\r\n".join([
    "From: " + fromaddr,
    "To: " + ", ".join(toaddrs),
    "Subject: FYI: The SDE has been backed up on " + day + "/" + month + "/" + str(time.year) + " at " + hour +":" + minute,
    "", ""])
sendEmail.sendEmail(fromaddr,toaddrs,msg)