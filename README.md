igsql
=====

Python module for storing Instagram data in a Postgres database and operating on it via SQLAlchemy


License and thanks
==================
Copyright 2014-2015 Karl Ward

This example code and explanatory text is licensed under the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See the file LICENSE for details.

This code was created within Gilad Lotan's Social Data Analysis course at NYU ITP during Fall 2014.  Respect and gratitude is due to Gilad.  

Jeff Ong and Kyle Greenberg helped refine and test these instructions. 

Overview
========

This example code demonstrates the following: 
- connecting to the Instagram search API
- downloading media posts that match a search
- storing those media posts in a Postgres database
- storing related information (user, location) associated with each media in separate, related tables in a Postgres database
- accessing the database using the SQLAlchemy object relational mapper (ORM), which allows you to do your data manipulation in Python rather than SQL
- writing a GEXF graph file from the data in your database

Each of these topics is only briefly introduced.  This should get you on your way toward using these tools in your own projects.  Don't expect this code to make you a master of SQL, SQLAlchemy, ORM, or Python.  Or Instagram.  Why do you want to be a master of Instagram anyway?

The PostgreSQL database is used in this example because of its superior handling of Unicode (e.g. Emoji, Chinese, many non-Western languages).

Installation/configuration
==========================

Install PostgreSQL database server
----------------------------------

Go to [http://postgresapp.com/](http://postgresapp.com/) and install the app on your machine.  These instructions assume that you'll install Postgres 9.4.  Some adjustments will need to be made in your $PATH if you use a different version.

Start up Postgres.  You can configure Postgres to start automatically, or you can start it whenever you need it.

Optional pro step: create a Python virtualenv
---------------------------------------------

If you have virtualenv, then in Terminal, create a new virtual environment for this program: 

    mkdir -p ~/venv
    cd ~/venv
    virtualenv igsql
    source ~/venv/igsql/bin/activate

Note: if you set up a virtualenv, remember to use it throughout this example. 

Install dependencies with pip
-----------------------------

In Terminal: 

    export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/9.4/bin
    pip install psycopg2 SQLAlchemy networkx python-instagram

Note: it's necessary to temporarily add the Postgres directory to your PATH environment variable, just so psycopg2 gets built properly by pip.  You can add it to your PATH permanently if you like, but you don't need to. 

Create a database
-----------------

Once you have Postgres running, you should see an elephant in the Finder bar at the top of the screen.  Click on the elephant and choose "Open psql".   You'll see a new Terminal window, but this one isn't running Unix.  Instead it is psql, the Postgres SQL command interface.  You need to run the following commands: 

    CREATE USER igsql WITH PASSWORD 'igsql';
    CREATE DATABASE igsql OWNER igsql;

That's it for psql, unless you want to muck around with the SQL directly.  

Get the igsql code
---------------------

If you don't have it already, get the igsql code from Git: 

    mkdir -p ~/Code
    cd ~/Code
    git clone https://github.com/karlward/igsql.git

Setup your database schema
--------------------------

Before you can use the database you created, you have to tell Postgres what kind of data you want to store in it.  Luckily, SQLAlchemy does most of the work for you, you just have to run one Python function.  In Terminal: 

    cd ~/Code/igsql
    python
    import igsql.database
    import igsql.model
    igsql.database.init_db()
    exit()

The last command exits from the python interpreter, bringing you back to the shell prompt.

That should have setup your database schema, which means you have an empty database that is ready to store data in the right format.  

Add your Instagram keys and search string(s)
------------------------------------------

You have to modify one file to use this code.  That file is: 

    ~/Code/igsql/load-stream.py

You need to set the following variables to the appropriate values:

    client_id = 'secret'
    client_secret = 'secret'
    search_tag = 'aiweiwei'

search_tag is a comma separated list of strings.  The search_tag string is documented in the Instagram client API, [https://github.com/Instagram/python-instagram#data-retrieval](https://github.com/Instagram/python-instagram#data-retrieval).  The tag search endpoint is described at [http://instagram.com/developer/endpoints/tags/](http://instagram.com/developer/endpoints/tags/).

Run the load-recent-media-by-tag.py script
-----------------------------

    cd ~/Code/igsql
    python load-recent-media-by-tag.py

This script accesses the tags endpoint API, searching backward through time to download every Instagram post that matches the tag.  Note that this script saves the URL of every post, but does not download the media itself. 

Run the write-gexf.py script
----------------------------

    cd ~/Code/igsql
    python write-gexf.py

This script creates a GEXF file for a bipartite graph, with media as one type of node, and users an another type of node.  Media are linked to users based on likes.  Though this is a bit of a contrived example, it shows the power that you get when you access the data through SQLAlchemy.  For example, if you want to iterate through all the media, that's relatively simple: 

    for m in db_session.query(Media).all():

Or just the most recent 500 media: 

    from sqlalchemy import desc
    for m in db_session.query(Media).order_by(desc(created_time))[0:500]:

If you want to access the users who liked a particular media post:

    m.likes

If you want to see the user who posted a particular media post:

    m.user


Also, notice that the load-stream script stores the entire JSON for each media in the media object's data field: 

    data = json.loads(m.data)

Or iterate through all the users you have seen, instead of all the media:

    for u in db_session.query(User).all():

And access the media you have captured for each user: 

    u.media

Poke around in the igsql model to learn how to roll your own
---------------------------------------------------------------

    cd ~/Code/igsql/igsql
    open model.py

Learn more about SQLAlchemy
---------------------------

[http://docs.sqlalchemy.org/en/rel_0_9/](http://docs.sqlalchemy.org/en/rel_0_9/)

Learn more about SQL
--------------------

[http://www.postgresql.org/docs/9.4/static/](http://www.postgresql.org/docs/9.4/static/)

