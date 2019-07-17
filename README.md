# Feature Request App

>This is an implementation of the assignment for a request feature app
The app is a single page application that uses KnockoutJS on front-end
side, and Flask, SQLAlchemy for the RESTFul back-end. In addition
to all project requirements, Google auth, CSRF protection, HTTP
authentication were enabled as well.

## Install

### Required soft

1. install [GIT](https://git-scm.com/downloads).
2. install [Python 2.7.14](https://www.python.org/downloads/release/python-2714/)

### Upload and run

After required soft are installed, enter into terminal the following
commands:
```
git clone https://github.com/DudkinON/feature_request_app

cd feature_request_app
```

then, on Mac OS: use [installer](https://www.python.org/downloads/release/python-2715/)

on Windows: use [installer](https://www.python.org/downloads/windows/)

on Linux:
```
sudo apt-get install python-pip
```
how to install python on defferent OS: [read](https://www.python.org/download/other/)

after python will installed, make sure that you have correct version:

```
python --version
```

you should see the following output:

`Python 2.7.10`

a version can be older but not 3+ or newer.

##### install virtual environment

In your console type:

```
python -m pip install --user virtualenv
```

to be sure that virlual environment was installed type:

```
pip show virtualenv
```

more information you can find in [official documentation](https://virtualenv.pypa.io/en/stable/)

then create virtual environment:

```
sudo python -m virtualenv env
```

on Mac OS or Linux type:
```
source env/bin/activate
```

on Windows OS type:
```
.\env\Scripts\activate
```

> This command will run virtual environment.

##### install requirements

and finally install requirements for application

```
sudo pip install -r requirements.txt

```

##### Run application

Then run app with following command:

```
python run.py
```

> After it will run, and you'll see text like this:

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 121-184-468
```

> Go to [open app](http://localhost:5000)

## Configuration

> This documentation is for the configuration of Google authorization,
you can skip this if you don't plan to use Third-party OAuth.


Open file ```feature_request_app/app/secrets/client_secrets.json```
and edit values of: **client_id**, **project_id**, **client_secret**, or
if you familiar with Google OAuth. Or just replace the file with yours
**Do not change file name**.

In directory "templates" find file "head.html". In file "head.html" find
following code:
```html
<meta id="google-app-id"
    data-key-api="API_KEY"
    data-clientid="OAuth_client_ID"
    data-scope="openid email"
    data-redirecturi="postmessage"
    data-accesstype="offline"
    data-cookiepolicy="single_host_origin"
    data-approvalprompt="force">
```
and replace the values with your data. To learn more about each
parameter, read [official documentation](https://developers.google.com/api-client-library/).

## Settings

Application for database settings and secret key uses the following file:
```feature_request_app/app/secrets/keys.py``` if you use
PostgreSQL as database edit the file with your database settings.
then, in file: ```feature_request_app/app/settings.py```, change
```POSTGRES = False``` to ```POSTGRES = True```
otherwise, the SQLite will be used as a database.

### Other settings

In file: ```feature_request_app/app/settings.py``` are several
variables:

```app_host``` - IP address where you want to user app

```app_port``` - port where will run app

```app_debug``` - if true will run Flask debug

```BASE_DIR``` - root directory of app

```SECRETS_DIR``` - define secrets folder for the app

```POSTGRES``` - if True app will use PostgreSQL as database

```CONNECT_SETTINGS``` - configuration string for PostgreSQL

```DB_FILE_NAME``` - file name of SQLite database

```SAME_THREAD``` - if true will checks same thread for SQLite db

```HOST``` - define host for unittests

```CREDENTIALS``` - define user credentials for unittests


## Used technologies

* Server Side Scripting: Python 2.7.10
* Server Framework: Flask 1.0.2
* ORM: Sql-Alchemy 1.2.7
* JavaScript: KnockoutJS 3.4.2
* Database: PostgreSQL 9.5

## Testing

> App passes test on both databases PostgreSQL and SQLite

#### Running tests

To run the tests you have to run the application. To do
this read the "Installation guide" above.

Open a terminal window in root application directory and run
your virtual environment

on Mac OS or Linux type:
```
source env/bin/activate
```

on Windows OS type:
```
.\env\Scripts\activate
```


then type into the terminal the following commands:

```
python app_tests.py
```

> NOTE: When you run the tests, your application has to be running

## Additional information

1. This application uses open source frameworks and libraries.

2. Decoupled backend and frontend, Single Page Application frontend
communicates with RESTFul backend by AJAX queries.

3. Tests imitate user behavior for each link. Additionally, each
function is tested.

4. Frontend side is implemented with Responsive Interface. The app
looks good on desktop and mobile devices.

5. Frontend side uses Knockout JS MVVM framework for
implementing Single Page Application.

#### Backend server

> The app deployed on AWS

**IP address:** 35.169.195.44

**URL:** [Feature Request App](https://feature-request-app.ml/)

##### Installed apps

* Ubuntu - OS (version 16.04)
* Apache - HTTP server (version2.4)
* Python - Programming Language (version 2.7.12)
* PostgreSQL - Database (version 9.5)
* Python Framework and libraries [list](requirements.txt)


##### Configuration

* Configured SSH access changed port to `2222`
* Configured AWS firewall and Ubuntu firewall
* Configured HTTP server Apache
* Disabled .htaccess support in Apache
* Turned on HTTP 2.0
* Configured HTTPS protocol
* Configured Flask application as a WSGI app
* Configured database server PostgreSQL

## License

This application sharing under [MIT](LICENSE) license, all used
frameworks and libraries have thyself license type.
