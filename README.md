Natural Language Interface (NALIR) - Python Implementation
--------
This project is a **NALIR** (Natural Language Interface for Database Systems) implementation in python.
The orginal source code was written in java, and it is [here](). To get more knowledge of how NALIR works (its components and how they work together), we've decide to implement our own version in python code, a more modern language then JAva. Python has more modern NLP libraries and it can help us in to improve the
NALIR algortithms. The idea for doing this commings out from Altigran supervising Brandell Cássio (graduate student) and Rafael(undergraduate Student) in their research themes.  

This project follows the [Google Python Code Style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)


How to run  NaLIR Jupyter Notebook?
----


## Setup database
First, you need a running MySQL instance available into your local machine or in a remote host.
Then, you need create a database with the dump listed [here](https://drive.google.com/drive/folders/0B-2uoWxAwJGKY09kaEtTZU1nTWM). The file that you need use to download is `MAS.sql`. After downloading the dump file you should run

``` bash
    $ mysql -D mas -u <user> -p < /path/to/MAS.sql
```

After that, you need to run `setup_mas.sql` in `zfiles`. This .sql has a sort of metadata relations that MAS needs to run properly. You going to run as the same way that
you ran the `MAS.sql`

``` bash
    $ mysql -D mas -u <user> -p < ./zfiles/setup_mas.sql
```

## Download Jars

After setting up MySQL database, you need to download the jars file needed to run NaLIR. These JARS are needed to run the Stanford Parser. You can download the jars [here](https://drive.google.com/file/d/1ggwTbEQsYHb0idMpr0qWvKjk7ulSJQTy/view). Once you downloaded, you need to unzip the jars file to use it in NaLIR build.
``` bash
    $ unzip /path/to/jars.zip
```

## Install Graphviz

After downloading the required jars, you also need to install Graphviz ([download page](https://www.graphviz.org/download/)), which is used to render the dependency trees.

## Setting up the environment

``` bash
   (venv) $ pip install -r requirements.txt
```

## Setting up the configuration object

After unzip the jars, you need to put the path where you extract the jars into the configuration object that are in the Jupyter.

```json
{
    "connection":{
        "host": "localhost",
        "password":"password",
        "user":"user",
        "database":"mas"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"path/to/zfiles",
    "jars_path":"/path/to/jars"
}
```
