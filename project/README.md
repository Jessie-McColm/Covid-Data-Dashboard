<h1>Online covid dashboard</h1>

<p>Welcome to the README for this online covid dashboard! This project aims to provide
its users with useful information pertaining to the current coronavirus pandemic. 
It is set up to provide users with statistics about the current spread of the virus 
in their local area and nation (within the UK), and also shows users news articles about 
the coronavirus. Users can edit their location and what search terms they want to use
to find article, and the information on how to do this can be found in the configuration file
part of the README. </p>

<h2>Set up:</h2>

<p>The following libraries must be imported to run this project:</p>
<ul>
<li>flask</li>
<li>sched</li>
<li>uk_covid19</li>
<li>requests</li>
</ul>
<p>They can be installed by typing "pip install 'package name'" into the command line.</p>

<h2>Use:</h2>

<p>To use this project you must first register for the news API at https://newsapi.org/ and get an API key. You must then enter this API key into the config file. This file is called config_file.json. Open the file in notepad and change the text "Enter your API key here:": to the API key. Make sure that the speech marks surrounding the text remain, and ensure that there are no spaces.</p> 

<h3>Changing news search terms:</h3>

<p>In the config file, altering the text after "Search terms:": will change the news articles that will be displayed. </p>

<h3>Changing Location</h3>

 <p> To set the location to match where you live, change the text after "Location:": You can also change the nation if you don't live in England by changing the text after "Nation:":. To find more information about locations and location types, go to <a href="https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/pages/" </a> link </p>


<h2>Credits:</h3>

<p>Here is a list of sites that helped me make this project </p>