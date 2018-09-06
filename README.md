# SDE-Backup
Written by Ryan Crow

Creates a backup of a series of Arc SDE databases and emails a series of users when it is completed.

In order to run this script you will have to make a copy of the backupParameters_exmaple.xlsx and strip off the "_examples" part. In the script you will have to input the path to this file. You will also have to populate both the "dbs" and "email" sheets. Note that the password you need to input in the "email" sheet is an application specific password that you need to set up in this case through google (see https://support.google.com/mail/answer/185833?hl=en). Also make sure you populate to "toaddrs" variable in the script with a list of email addresses you want the email sent to.
