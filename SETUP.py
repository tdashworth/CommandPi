___author___  = "TDAashworth"
___website___ = "tdashworth"
___version___ = "1.0"

# IMPORTS --------------------------------------------------------------------
import os, time, sqlite3

# GLOABAL VARIABLES ----------------------------------------------------------
location    = "/home/pi/CommandPi/" # Location file's folder

# CONNECT TO DB --------------------------------------------------------------
connect = sqlite3.connect(location+"commandPi.db")
cursor = connect.cursor()
try:
    data = cursor.execute("SELECT * FROM Settings")
except:
    cursor.execute("""CREATE TABLE Commands(
	        `Hotword`	TEXT,
	        `Command`	TEXT)""")
    cursor.execute("""CREATE TABLE `Settings` (
	        `FirstRun`	INTEGER,
	        `Username`	TEXT,
	        `Password`	TEXT,
	        `WaitTime`	REAL,
	        `Alert`	INTEGER,
         	`AlertAddress`	TEXT)""")
    cursor.execute("INSERT into Settings VALUES (1,'','',120,0,'')")
    connect.commit()
    
    
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

# Login ======================================================================
def login():
    global username, password
    print("Login:")
    print("Plase enter the details of a GMail account below.")
    print("Note: enter email address without '@gmail.com'.")
    username = input("Username: ")
    password = input("Password: ")


    cursor.execute("UPDATE Settings SET Username = (?) WHERE FirstRun = (?)",(username,1,))
    cursor.execute("UPDATE Settings SET Password = (?) WHERE FirstRun = (?)",(password,1,))
    connect.commit()

# Command DB =================================================================
def comDB():
    os.system("clear")
    print(" ---------------- LAN PI ----------------")
    print("""
What would you like to do:
1) View commands?
2) Add command?
3) Edit command value
4) Edit command hotword
5) Remove command?
6) Back
""")

    task = input("Enter number: ")
    print("")

    os.system("clear")
    if task == "1": # --------------------------------------------------------
        print("Commands:")
        cursor.execute("SELECT * FROM Commands")
        r=1
        while True:
            row = cursor.fetchone()
            if row == None:
                break
                
            print (r,": ",row[0],"\t\t",row[1])
            r+=1
            
        print()
        back = input("\nPress enter to go back...")
    elif task == "2": # ------------------------------------------------------
        print("Add Command:")
        hotword=input("Command hotword: ").lower()
        command=input("Command: ")
        cursor.execute("INSERT INTO Commands VALUES (?, ?)", (hotword, command))
        connect.commit()
    elif task == "3": # ------------------------------------------------------
        print("Update a command value:")
        hotword=input("Command hotword: ").lower()
        command=input("Command: ")
        cursor.execute("UPDATE Commands SET Command = (?) WHERE Hotword = (?)",(command, hotword))
        connect.commit()
    elif task == "4": # ------------------------------------------------------
        print("Update a command hotword:")
        command=input("Command: ")
        hotword=input("Command hotword: ").lower()
        cursor.execute("UPDATE Commands SET Hotword = (?) WHERE Command = (?)",(hotword, command))
        connect.commit()
    elif task == "5": # ------------------------------------------------------
        print("Delete command:")
        hotword=input("Command hotword: ").lower()
        command=input("Command: ")
        try: 
            cursor.execute("DELETE FROM Commands WHERE Hotword = (?) AND Command = (?)",(hotword,command))
            print("Deleted!")
        except lite.Error:
            print("Hotword and Command do not match")
        connect.commit()
    elif task == "6": # ------------------------------------------------------
        os.system("clear")
    else:
        comDB()

# Email Alert ================================================================
def emailAlert():
    global alert, alertAddress
    
    print("""
Email alerts are message sent to a set email address
informing you of any commands sent to the pi.

What would you like to do:
1) Enable email alerts
2) Disable email alert
3) Set alert email address
4) Back
""")

    task = input("Enter number: ")
    print("")

    if task == "1":
        alert = True
        if len(alertAddress) < 3:
            alertAddress = input("Email address: ")
        emailAlert()
    elif task == "2":
        alert = False
        emailAlert()
    elif task == "3":
        alertAddress = input("Email address: ")
        emailAlert()
    elif task == "4":
        os.system("clear")
    else:
        emailAlert()

# ----------------------------------------------------------------------------
while True:
    os.system("clear")
    print("\t\t------ Command Pi ------")

    print("""
What would you like to do:
1) Change login details?
2) Computer DB
3) Change wait time
4) Email alerts
5) Auto run
6) Reset ALL
7) Run software
8) Exit
""")

    task = input("Enter number: ")
    os.system("clear")
    print("\t\t------ Command Pi ------")

    if task == "1":
        login()
    elif task == "2":
        comDB()
    elif task == "3":
        changeWait()
    elif task == "4":
    	emailAlert()
    elif task == "5":
    	autoRun()
    elif task == "6":
    	print("Resetting all...")
    	os.system("rm "+location+"log.txt")
    	os.system("rm "+location+"commandPi.db")
    	clear
    	os.system("python3 "+location+"SETUP.py")
    elif task == "7":
        os.system("python3 "+location+"COMMANDPI.py")
        break
    elif task == "8":
        exit()
    else:
        os.system("clear")

    
