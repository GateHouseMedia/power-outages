
# Power outage tools

This is a collection of tools used to monitor power outages. The initial release included Florida Power & Light, Duke Energy and North Carolina EMC customers in Florida, South Carolina, North Carolina, Indiana, Ohio and Kentucky.

This is a sister project to Hurricane Tools, found at https://github.com/GateHouseMedia/hurricane-tools

There are three major components here:
* Scrapers that can be scheduled to repeatedly run, saving results in local SQLite database files.
* Programs to extract data from the database and feed it in a friendly format for:
* Web pages that can be embedded as widgets to show your outages.

Because these are tracking power outages, you'd ideally have them running before you'd expect significant power outages. You'd also be wise to run them from a server that is  highly unlikely to experience power outages.  A $5/mo. DigitalOcean droplet has proven itself more than capable of serving a fairly substantial web volume from these widgets, while also doing the scraping. You'll want to set these up on a server with HTTPS, as you'll almost certainly be iframing widgets within HTTPS pages. Think out your infrastructure.

## Installation

* Clone repo.
* Set up for Python 3, e.g., *pip install -r requirements.txt
* Rename config.py.sample to config.py. Rename all your sample.db databases to just plain .db.
* Edit *config.py*. More on this below.
* If publishing for a storm, build a directory on your web server, prepare your HTML and move in your Javascript files.
* Set up a crontab or Scheduled Task or whatever your system has to regularly get the data. A sample crontab line:

`0,30 * * * * cd ~stucka/power-outages && /usr/bin/python3 getpower.py`

## File descriptions

**config.py** -- Simple configuration script. All the variables are documented. Make sure your web folder has a trailing slash.

**runeverything.py** -- Python script to run all the scrapers in parallel. You may wish to edit this the one time, e.g., if you're only interested in Ohio power outages, you have no need to call the Florida Power and Light scrapers.

**somethingreport.py** -- Individual scrapers for each power company. There are two scrapers for Florida Power & Light because FPL has two different reporting processes. Scrapers *should* be fairly stable and not need editing.

**somethingjsoner.py** -- Configuration files controlling how data is moved from the databases to JSON files. Basically, you'd want to make sure your community is in here, and pulling the correct data.

**samplehtml** -- Sample HTML files and supporting files to work with the JSON output.

- **JS folder** -- You'll want to use these files with the sample HTML. They're set up to be called from inside the "js" folder of your main HTML build directory, e.g., /something/stormnamehere/js.

- **template-counts.html** -- Show power outages by number of customers without power. This is probably what you want, unless your community has been absolutely clobbered.

- **template-percentage** -- Show power outages by percentage of customers without power. Not all scrapers will work with this because not all scrapers know how many customers are in an area.  If your area has been blasted -- like nearly all FPL customers were without power after Hurricane Irma -- you may want to remove the comment marks at the beginning of this line, to force the scale to go to 100 percent. `//                        max: 100,`

## OK, now what?

If you need to implement widgets, you can try it something like this -- watch whether the quote marks come through right:

&lt;iframe src="https://some.server.com/misc/somestorm/nc-fayetteville-duke.html" is="responsive-iframe" width="100%" &gt; &lt;/iframe&gt; 
&lt;script src="https://some.server.com/misc/somestorm/js/responsive-frame.js" &gt; &lt;/script&gt;

If you're on a GateHouse Media CMS, you'll probably want something like this:

[gh:iframe src="https://irma.gatehousemedia.com/misc/somestorm/nc-fayetteville-duke.html"  is="responsive-iframe" width="100%"][/gh:iframe][gh:script src="https://irma.gatehousemedia.com/misc/somestorm/js/responsive-frame.js"][/gh:script]

## Other work

Simon Willison, @simonw, has some data handling tooling for PG&E power outages in California available at https://github.com/simonw/pge-outages , with historical data available through the git commit history. More details are available at https://simonwillison.net/2019/Oct/10/pge-outages/

Jesse Hazel, @jwhazel, offers up this Kentucky site for seeing all statewide outages: https://psc.ky.gov/ors/PublicInfo_OutageIncidents.aspx


### Special thanks

This particular project owes much to Dorian, an awful 2019 hurricane that pummeled The Bahamas and caused major worries along a substantial hunk of the eastern seaboard.

We are particularly indebted to Thomas Wilburn [@thomaswilburn](https://github.com/thomaswilburn), who identified a critical obscure operation needed to get one scraper working, and who also drafted the [Seattle Times' responsive-frame code](https://github.com/seattletimes/responsive-frame) incorporated into the sample HTML of this project.

This project has its origins in stuff tied to Hurricane Irma in 2017, with all the data viz component handled by Mahima Singh [@amiham-singh](https://github.com/amiham-singh) and the first scraper being built by Mike Stucka.

### Contributions welcomed

Want us to adopt your scraper? Need something? Let's talk!
