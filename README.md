<h1>Online covid dashboard</h1>

<p>Welcome to the README for this online covid dashboard! This project aims to provide
its users with useful information pertaining to the current coronavirus pandemic. 
It is set up to provide users with statistics about the current spread of the virus 
in their local area and nation (within the UK), and also shows users news articles about 
the coronavirus. Users can edit their location and what search terms they want to use
to find article, and the information on how to do this can be found in the configuration file
part of the README. More documentation can be found in \project\docs\_build\html </p>

<h2>Set up:</h2>

<p>The following libraries must be imported to run this project:</p>
<ul>
<li>flask</li>
<li>sched</li>
<li>uk_covid19</li>
<li>requests</li>
</ul>
<p>They can be installed by typing "pip install 'package name'" into the command line. Use python version 3.8 or above</p>

<h2>Use:</h2>

<p>To use this project you must first register for the news API at <a href="https://newsapi.org/">https://newsapi.org/ </a> and get an API key. You must then enter this API key into the config file. This file is called config_file.json. Open the file in notepad and change the text "Enter your API key here:": to the API key. Make sure that the speech marks surrounding the text remain, and ensure that there are no spaces.</p> 
<p> Once you have set you API key, you should run the python file called "main.py" in the command line by typing "python main.py". Make sure that you are in the same directory as the file first. Then open a web browser and navigate to <a href="http://127.0.0.1:5000/index">http://127.0.0.1:5000/index </a>  </p>

<h3>Changing news search terms:</h3>

<p>In the config file, altering the text after "Search terms:": will change the news articles that will be displayed. </p>

<h3>Changing Location:</h3>

 <p> To set the location to match where you live, change the text after "Location:": You can also change the nation if you don't live in England by changing the text after "Nation:": . To find more information about locations and location types, go to <a href="https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/pages/">https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/pages/ </a> </p>


<h2>Credits:</h3>

<p>Here is a list of sites that helped me make this project:</p>
<ul>
<li><a href="https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/pages/">The site for the covid API </a></li>
<li><a href="https://newsapi.org/">The site for the news API </a></li>
<li><a href="https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world">A useful flask tutorial</a></li>
<li><a href="https://werkzeug.palletsprojects.com/en/2.0.x/utils/">Helped redirect the site after a request</a></li>

</ul>