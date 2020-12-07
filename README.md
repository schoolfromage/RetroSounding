

This repository is a submisison by Austin Cari, Steven Arbuckle and Daniel Belousov for CS 454 Information Retrieval w/ Prof. Ben McCamish at WSU Vancouver.

RetroSounding is a web application that uses Flask as a frontend tool to dynamically create web pages using results and records from a Whoosh! Index on the backend that is storing data about retro-style video games. Our database contains information about video game titles from as early as Pong up to the year 2000. To put that into perspective, the extremely successful franchise The Sims was first released by Maxis on Feburary 4th, 2000.

This project has been split into a frontend, where the HTML templates and flask scripts live, along with static content like images and stylesheets. The backend portion contains our web scraper and our raw scraped data, along with our Whoosh! index and whoosh scripts. When the flask app is started, we will create an instance of a Whoosh! object that can query the index we created and return results to the user in a web browser. Users are able to click on individual results and see in-depth information about any title in our database.

===How to Run===
1. Make sure you have the correct dependencies installed

  a) Install dependencies using pip MacOS, Linux, Commpand prompt: 

  `pip3 install flask` and then
  `pip3 install whoosh`
  
  b) Windows Powershell: 

  `python3 -m pip install flask` and then
  `python3 -m pip install whoosh`
  

2. Boot up the app from the root directory using: `python3 frontend/__init__.py`

3. Open your browser and go to http://127.0.0.1/5000/

===How to use===
All you have to do is enter a search term into the search bar and you will see a list of results to choose from. Keep entering queries until you find the game you're looking for.
