# Retro Sounding

This repository is a submisison by Austin Cari, Steven Arbuckle and Daniel Belousov for CS 454 Information Retrieval w/ Prof. Ben McCamish at WSU Vancouver.

RetroSounding is a web application that uses Flask as a frontend tool to dynamically create web pages using results and records from a Whoosh! index on the backend that is storing data about retro-style video games. Our database contains information about video game titles from as early as Pong up to the year 2000. To put that into perspective, the extremely successful franchise The Sims was first released by Maxis on Feburary 4th, 2000.

This project has been split into a frontend, where the HTML templates and flask scripts live, along with static content like images and stylesheets. The backend portion contains our web scraper and our raw scraped data, along with our Whoosh! index and whoosh scripts. When the flask app is started, we will create an instance of a Whoosh! object that can query the index we created and return results to the user in a web browser. Users are able to click on individual results and see in-depth information about any title in our database.

=== How to Run ===
1. Make sure you have the correct dependencies installed

     * On MacOS, Linux, Command prompt: 

        `pip3 install flask whoosh`

    * On Windows Powershell: 

      `python3 -m pip install flask whoosh`

2. Run the app from the root directory with: 

      `python3 frontend/__init__.py`

3. Open your browser and go to `http://127.0.0.1/5000/`

=== How to use === 

Just search for a game and keep searching until you find it

