# SDE-Backup
Written by Ryan Crow, USGS

Creates a backup of a series of Arc SDE databases, compresses them, and then emails a series of users when it is completed.

In order to run this script you will have to make a copy of the backupParameters_exmaple.xlsx and strip off the "_examples" part. In the script you will have to input the path to this file. You will also have to populate the "dbs", "email", "sde", and "emailrecipient" sheets. Note that the password you need to input in the "email" sheet is an application specific password that you need to set up in this case through google (see https://support.google.com/mail/answer/185833?hl=en).

In addition to backing up the databases the script also checks for current connections to the databases, which requires an sde connection, and if there are none it compressed the databases. Finally the scipt emails users and the subject of the email indicates when the backup occurred and which databases were compressed. 
