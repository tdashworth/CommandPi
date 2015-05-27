___author___ = "TDAashworth"
___website___ = "tdashworth"
___version___ = "1.0"

# IMPORTS --------------------------------------------------------------------
import imaplib, email, os, time, sqlite3, smtplib

# GLOABAL VARIABLES ----------------------------------------------------------
location = "/home/pi/CommandPi/"
#location = ""# Location file's folder
messages = ""
imapServer = None
count = 0
mailBodies = []
mailFrom = []

# CONNECT TO DB --------------------------------------------------------------
connect = sqlite3.connect(location+"commandPi.db")
cursor = connect.cursor()

# GATHER SETTINGS ------------------------------------------------------------
data = cursor.execute("SELECT * FROM Settings")
settings = (cursor.fetchone())

firstRun     = int(settings[0])
username     = settings[1]
password     = settings[2]
waitTime     = float(settings[3])
alert        = int(settings[4])
alertAddress = settings[5]

if firstRun == 1:
  logFile = open(location+"log.txt", "w")
  firstRun = 0
  cursor.execute("UPDATE Settings SET FirstRun = (?) WHERE FirstRun = (?)",(1,0,))
  connect.commit()
  logFile.close()

# LOG IN TO MAIL =============================================================
def accessAccount():
    global imapServer, messages
    #print("Accessing account...")
    try:
        imapServer = imaplib.IMAP4_SSL("imap.gmail.com") # Connect to imap server
        
        try:
            imapServer.login(username, password) # Logins in to the account
            print("Logged in.")
            messages += "\nLogged in!"
        except:
            # Login error messages
            print("Fail to login.")
            messages += "\nPlease check your network and login details."
            #print("Connecting to internet. Trying in 2 minuets...")
            time.sleep(120.0)
            accessAccount()
    except:
        # Connection error message
        messages += "\nError in code. Please contact developers. \nPROGRAM TERMINATED"
        exit()

# CHECK FOR NEW MAIL =========================================================
def checkForMail():
    global messages, imapSever, mailBodies
    #print("Checking mailbox...")
     
    imapServer.list()
    imapServer.select("INBOX") # Select mailbox

    # Search for mail
    typ, data = imapServer.search(None, "UNSEEN") # select unread mail
    for num in data[0].split():
        #print("Mail found...")
        #messages += "\nMail found..."
        typ, data = imapServer.fetch(num, "(RFC822)")
        rawEmail = data[0][1] # build message
        imapServer.close()

        emailMessage = email.message_from_string(rawEmail.decode('utf-8'))

        mailFrom.append(emailMessage['From'])

        for part in emailMessage.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)
                mailBodies.append(body.decode('utf-8').lower())
            else:
                continue
      
    # Delete mail from mailbox
        imapServer.select("inbox")
        typ, data = imapServer.search(None, "ALL")
        for num in data[0].split():
            imapServer.store(num, "+FLAGS", "\\Deleted")
        imapServer.expunge()
    #print(mailBodies)

# SEARCH MAIL FOR COMMANDS ===================================================
def checkForCommands():
    global messages, mailBodies

    # Get list of current hotwords from DB
    cursor.execute("SELECT Hotword FROM Commands")
    data = cursor.fetchone()
    hotwords = []
    commands = []

    x=0
    while data != None:
       data = str(data)
       data = data[2:len(data)-3]
       hotwords.append(data)
       data = (cursor.fetchone())
       x+=1

    # Search file for hotwords
    for hotword in hotwords:
        if hotword in str(mailBodies):
            #print("Hotword found...")
            #messages += "Hotword found..."
            commands.append(getCommand(hotword))
    if "stop" in mailBodies:
        commands.append("stop")
    
    if len(commands) > 0:
    	messages += "\nFound command(s): \n" + decodeList(commands,", ")
        
    mailBodies = []
    
    return commands

# RETRIEVE COMMAND FOR DB ====================================================
def getCommand(hotword):
    cursor.execute("SELECT Command FROM Commands WHERE Hotword=?", (hotword,))
    command = str(cursor.fetchone())
    command = command[2:len(command)-3]
    return(command)

# SEND ALERT MAIL ============================================================
def sendAlert(message):
    fromaddr = username+"@gmail.com"
    toaddrs  = alertAddress
    msg = ("""From: Pi Commander <"""+username+"""@gmail.com>
To: User <"""+alertAddress+""">
Subject: CommandPi - Received command - Log
** CommandPi - Received command - Log **
"""+message)
       
    try:
        smtpServer = smtplib.SMTP("smtp.gmail.com:587")
        smtpServer.starttls()
        smtpServer.login(username,password)
        
        smtpServer.sendmail(fromaddr, alertAddress, msg)
        
        #print("Sending alert...")
        smtpServer.quit()
    except():
    	print("FAILED TO SEND ALERT")

# DECODE LIST ================================================================
def decodeList(array,space):
    string = ""
    for item in array:
        string += str(item) + space
    return string

# START SCANNING -------------------------------------------------------------
accessAccount()
while True:
    #print("\t\t------ Command Pi ------")
    count+=1
    #print("Count: ",count) # Prints current count
    checkForMail()
    logRecords = []
    commands = checkForCommands()

    for command in commands:
        if decodeList(command,"") == "stop":
            #run = False
            break
        else:
            currentTime = str(time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime()))
            try:
                output = os.popen(command).read()
                messages += "\n\n" + command + ": \n" + output
                logRecords.append(currentTime + ": " + str(command) + " - Executed. \n")
            except:
                messages += "\n\n'" + command + "' failed to execute."
                logRecords.append(currentTime + ": " + str(command) + " - Failed to execute. \n")
    
    logFile = open(location+"log.txt", "a")
    for logRecord in logRecords:
        logFile.write(logRecord)
    logFile.close()
    
    if alert == 1 and len(messages) > 0:
    	sendAlert(messages)
    	
    #print("Waiting for ",waitTime," seconds....")
    time.sleep(waitTime) # Stops loop for set time (s)
    #print(messages) # Prints meesages 
    messages = "" # Clears messages
    os.system("clear") # Clears shell














































