js-lib-sniper
=============

OWTF's JavaScript Library Sniper: A standalone tool for figuring out vulnerabilities from JavaScript library files, OWTF integration is minimal and mostly done from the OWTF repo.

Dependencies
-----------------

  * `Python >=26 <http://www.python.org>`
  * `PyQt > 443 <http://www.riverbankcomputing.co.uk/software/pyqt/download>`

Install
----------------
    git clone https://github.com/owtf/js-lib-sniper.git
    cd js-lib-sniper
    pip install -r requirements.txt

Usage
---------------
```
usage: js-lib-sniper.py [Options] {Target FILE}

︻デ┳═ー Detect old javascript libraries with vulnerabilities.

positional arguments:
  FILE                  javascript library

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         display the version and exit.
  -v, --verbose         show extended output
  -q, --quite           dont display to standard output.
  -y, --yes             assume Yes to all queries and do not prompt.
  -oN <file>            output in normal format respectively, to the given
                        filename.
  -oX <file>            output logs in XML format respectively, to the given
                        filename.
  --log <file>          output logs(errors, warnings) to the given filename.
  --jsdir <folder>      folder to scan for javascript files
  --files-from <file>   read the filenames(comma delimited) to be examined
                        from file
  --ignore <paths>      comma delimited list of paths to ignore
  --ignore-from <file>  read the paths(comma delimited) to be ignored from
                        file
  --proxy <url>         proxy url (http://some.sever:8080)
```

Feedback
-----------------
Open an issue [https://github.com/owtf/js-lib-sniper/issues](https://github.com/owtf/js-lib-sniper/issues) to report a bug or request a new feature. Other comments and suggestions can be directly emailed to the authors.








