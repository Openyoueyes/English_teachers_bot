Your Student Accounting Bot
=============================
Teachers bot - this bot allows you to keep track of students' payments to English tutors. If desired, it can be easily scaled or rewritten for any other subject.Helps track debtors and sends debt notifications to them on its own.

![menu](https://user-images.githubusercontent.com/105518519/209647150-6b3d26ad-3ff0-4054-8632-eeae9eaa87f2.png)


INSTALLATION
------------
There are two installation options.
- install locally
- run in docker containers (recommended)

Install locally:
- enter the necessary data in the .env file
- install and customize postgress db
- if you wont to start WEBHOOK , you need to get a ssl certificate and configure the nginx server on your vps and any name to the string "APP_NAME" from .env,  if you wont to start POLLING - make "APP_NAME" string empty.
- create virtualenv 
- install REQUIREMENTS

Install in docker containers:
- enter the necessary data in the .env file !!!YOU MUST CHANGE STRING "POSTGRES_HOST=db" !!!!
- if you wont to start WEBHOOK , you need to get a ssl certificate and configure the nginx server on your vps and any name to the string "APP_NAME" from .env,  if you wont to start POLLING - make "APP_NAME" string empty.Example settings nginx in bot_nginx_conf.

REQUIREMENTS
------------
I have collected the minimum and most necessary dependency package for the bot to work. 
All dependencies can be found in the file "requirements.txt".


QUICK START
-----------
Start locally:
- after installation and configuration according to the instructions, you need to activate the virtual environment with installed dependencies
- entry point "python3 start.py"

Start in docker containers:
- just go to the root directory of the application and write the command "docker-compose up --build -d" !!!!Attention!!! Certificate addresses and nginx settings may be different in my docker-compose and yours!! Pay attention to this!!!

WHAT'S NEXT
-----------
Please install the and join the resolution and add amendments. Thank you for your attention!!!
