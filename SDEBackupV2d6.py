import arcpy
import datetime
import pandas #Tested with version 0.19.1
import smtplib

#INPUTS
#!NOTE! the path to the following file needs to be changed for other system configurations
excelFile = r"\\igswzcwwgsrio\loco\Team\Crow\_Python\SDEbackup\backupParameters.xlsx"
toaddrs = pandas.read_excel(excelFile, sheet_name='emailRecipient')['emailAddresses'].tolist()

#OPTIONS
compressToo = True

def sendEmail(fromaddr,toaddrs,msg):
    print("Sending an email")
    params = pandas.read_excel(excelFile, sheet_name='email')
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

def datetimePrint():
    time = datetime.datetime.now() #Get system time
    if len(str(time.month))==1:
        month="0"+str(time.month)
    else:
        month=str(time.month)
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
    timeDateString = str(time.year) + month + day + "_" + hour + minute + "_" + second
    date = month + "/" + day + "/" + str(time.year)
    timestr = hour + ":" + minute
    return [timeDateString,date,timestr,time]

def checkAndDelete(CDpath):
    if arcpy.Exists(CDpath):
        print(CDpath +": Exists, Deleted")
        arcpy.Delete_management(CDpath)
    else:
        print(CDpath +": Does Not Exist")


connectionPath = arcpy.env.scratchFolder

timeDateString = datetimePrint()[0]
date = datetimePrint()[1]
time = datetimePrint()[2]
start = datetimePrint()[3]


params = pandas.read_excel(excelFile)
servers=params['SDE_server'].tolist()
dbs=params['SDE_db'].tolist()
prefix=params['Export_prefix'].tolist()
suffix=params['Export_suffix'].tolist()
filenames=[]
for index, file in enumerate(prefix):
    filenames.append(prefix[index] + timeDateString + suffix[index])
exportPaths=params['Export_path'].tolist()

sdeUser=pandas.read_excel(excelFile, sheet_name='sde').iat[0,0]
#print(sdeUser)
sdePassword=pandas.read_excel(excelFile, sheet_name='sde').iat[0,1]
#print(sdePassword)
emailSubject = "Subject: FYI: SDE backed up " + date + " at " + time
emailString = "The following users were connected: "
for i in range(0,len(servers)):
    print("Server: "+servers[i])
    print("Database: " + dbs[i])
    arcpy.env.overwriteOutput = True
    #An SDE connection is needed to get the list of connected users
    #The name of the connection can't be too long
    arcpy.CreateDatabaseConnection_management(out_folder_path=connectionPath,
                                              out_name="ConnectForBackupTo_" + servers[i].split(".")[0] + "_" + dbs[i],
                                              database_platform="POSTGRESQL",
                                              instance= servers[i],
                                              account_authentication="DATABASE_AUTH",
                                              username=sdeUser,
                                              password=sdePassword,
                                              database=dbs[i])
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

    if compressToo:
        print("Trying to  compress the DB")
        users = arcpy.ListUsers(arcpy.env.workspace)
        if len(users) > 1: #We just made a connection
            emailString = emailString + "\r\n" + "In DB: " + dbs[i]
            for user in users:
                userConnected = "Username: {0}, Connected at: {1}".format(user.Name, user.ConnectionTime)
                print(userConnected)
                emailString = emailString +"\r\n" + userConnected
            print("Did not compress, users connected")
            emailSubject = emailSubject + "; " + dbs[i]+ " not compressed"
            emailString = emailString + "\r\n\r\n"
        else:
            print("No one is connected to the SDE")
            arcpy.AcceptConnections(arcpy.env.workspace, False)
            arcpy.Compress_management(arcpy.env.workspace)
            arcpy.AcceptConnections(arcpy.env.workspace, True)
            print("Compression done")
            emailSubject = emailSubject + "; " + dbs[i]+ " compressed"

timeDateStringEnd = datetimePrint()[0]
end = datetimePrint()[3]
elapsed = end-start

emailSubject = emailSubject + "; Elapsed time: " + str(elapsed)

#Email addresses for use in sending emails
fromaddr = pandas.read_excel(excelFile, sheet_name='email').iat[0,0] #get email address from param file
toErrorAddrs = pandas.read_excel(excelFile, sheet_name='email').iat[0,0]

msg = "\r\n".join([
    "From: " + fromaddr,
    "To: " + ", ".join(toaddrs),
    emailSubject,
    "", emailString])
sendEmail(fromaddr,toaddrs,msg)