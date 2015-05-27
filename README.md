Command Pi  - Executing commands via emails.

I have designed and written a system to execute commands on my Raspberry Pi (B+) from an email.

I started off with wanting a boot my PC up before I get home. To do this I use "wakeonlan" but I still need to execute the command remotely. 

I wrote a python3 script which accesses a random gmail account for new mail, if so it reads the contents searching for pre-set "hotwords" from a DB. If a hotword is found it goes back to the DB to fetch the command. It then executes it then emails me back notifying me of its executing.

a) How can this be more efficient?
b) How can I convert this concept to a web app?  

Here is the source code. Go have fun with it.

Thanks in advance.

Tom﻿
