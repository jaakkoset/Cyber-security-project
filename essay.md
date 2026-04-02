Project I

I am referring to the OWASP 2025 list in this project.

LINK: https://github.com/jaakkoset/Cyber-security-project

INSTALLATION. The installation instructions are for Linux.

Clone the repository and navigate to it’s root directory. Then go the the application directory:

    $ cd project/

Create a virtual environment and start it:

    $ python3 -m venv virtual-env
    $ source virtual-env/bin/activate

Install the dependencies:

    (virtual-env) $ python3 -m pip install -r requirements.txt

Set up the database:

    (virtual-env) $ python3 manage.py migrate

You can add example data in the database (not required for the application to work):

    (virtual-env) $ python3 manage.py add_example_data

Start the application (at http://localhost:8000/polls/):

    (virtual-env) $ python3 manage.py runserver

The example data adds two users (username:password):

    bob:squarepants
    alice:redqueen

You can always delete the database (db.sqlite3) and recreate it using the migrate command.

FLAW 1. CSRF attack.

The flaw in in the save_poll route function:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L74-L113

The save_poll route function is vulnerable to CSRF attacks. If a user is logged-in and he visits a malicious website, that site can add polls without the users knowledge. This is possible because save_poll does not have any CSRF checks.

To demonstrate the attack, log in at http://localhost:8000/polls/. In a new terminal window, go to the csrf/ directory and run

    python3 -m http.server 9000

Then, in a new browser tab, open this page:

    http://localhost:9000/csrf_get.html

Reloading http://localhost:8000/polls/ will now reveal that a new evil poll has been added. The screenshot flaw1-before-terminal.png shows that the request to add the poll is not rejected, and the screenshot flaw1-before-browser.png shows that the “Evil poll” has been added.

The vulnerability is fixed by changing the save_poll function to use POST requests. Django automatically checks the CSRF token with POST requests. Lines 74 and 105-113 in save_poll have the fixed code commented out:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L74

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L105-L113

Also, the corresponding html form should be modified to send POST requests:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/templates/polls/create.html#L23

Now we can try reapeating the CSRF attack, but because we want to use POST requests this time, we should load the page

    http://localhost:9000/csrf_post.html

This time Django automatically checks the CSRF token and rejects the request. This can be seen from these screenshots:

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw1-after-terminal.png

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw1-after-browser.png

FLAW 2. Voting without logging in.

OWASP category: A01 Broken access control.

The source of the flaw is in the vote route function:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L44-L65

Voting should be possible only to users. The voting functionality is hidden from others in the UI, but by sending a POST request to the right address anyone can still vote. This flaw belongs to the

The vulnerability can be demonstrated by running the following code in a browser console:

var csrf_token = document.cookie.match(/csrftoken=([^;]+)/)[1]

fetch("/polls/6/vote/", {
method: "POST",
headers: {
"Content-Type": "application/x-www-form-urlencoded",
"X-CSRFToken": csrf_token
},
body: "choice=15"
})

This is illustrated in this screenshot:

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw2-before-browser_before_refreshing.png

The problem can be fixed using Django’s @login_required-decorator. This ensures that only logged in users can send requests to the route function. The one-line-fix is commented out here:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L44

FLAW 3. SQL injection

OWASP category: A05 Injection.

The source of the problem is in this part of the save_question function in database.py:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L30-L37

When creating a new poll, it is possible to inject SQL code into the question field. For example, injecting the following code results in two polls being created, one which has no choices and another which has no question, making it unclickable at the front page:

    No choices LOL", CURRENT_TIMESTAMP), ("", CURRENT_TIMESTAMP) --

The injection is illustrated in screenshot

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-before-injection.png

and the result is shown in screenshot

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-before-result.png

The problem can be fixed by sanitizing inputs. This is easy to do with sqlite’s parameter binding. The fixed code is commented out here:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L40-L48

After the fix, the input is treated as text and not as SQL code. This is illustrated in the screenshot

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-after.png

FLAW 4. Outdated dependency

OWASP category: OWASP A06 Outdated component.

The version of Django is set in the requirements.txt file:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/requirements.txt#L2

The version can also be checked from terminal:

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw4-before.png

The project uses the Django version 5.1.15, which is unsupported as is listed here:
https://www.djangoproject.com/download/

To fix the problem one should upgrade Django to a supported version. In this case it is possible to upgrade to the latest Django version without causing any problems in the application. To upgrade use this command:

    (virtual-env) $ pip install --upgrade django

Here is a view of the terminal after doing that:

https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw4-after.png

FLAW 5. Security misconfiguration

OWASP category: A02:2025 Security Misconfiguration.

User can intentionally cause an error, that reveals sensitive information about the server. This happens because the server is running in development mode, which shows overly infromative error messages. The revealed infromation can for example be used to find exploits. Here is the source of the problem:

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/config/settings.py#L27

One way to intentionally cause an error is by creating a tampered URL. Here is an example (note that the URL has spaces):

    http://localhost:8000/polls/save-poll/?question=How much do you sleep?&choice1=less than 8 hours.&choice2=at least 8 hours

The given url is missing choice3 and choice4. The application expects empty strings for missing choices, but when the variables are omitted entirely, the code raises an error when trying to access those keys in the request dictionary. The error happens at the following line, where “choice3” and “choice4” are hard-coded:

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L14

To fix the problem, the line 27 in config/settings.py should be changed to DEBUG = False:

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/config/settings.py#L26-L28

However, after setting DEBUG = False, Django does not anymore serve static files (the style.css in this case). To fix that, a middleware called Whitenoise has already been added to the projects dependecies. It requires some configuration in project/config/settings.py, but these settings are already in place and do not need to be changed:

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/config/settings.py#L31

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/config/settings.py#L49

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/config/settings.py#L125-L126

After the fix, when the we use the URL link above, the error shown does not reveal anything it should not, as shown here:

_url-link-to-screenshot_

Lastly, we should also prevent the error from happening altogether, by validating the request data and returning an HTML status code for the user. (This aspect of the problem belongs more closely to the A10:2025 Mishandling of Exceptional Conditions category.) A fix for this is commented out here:

https://github.com/jaakkoset/Cyber-security-project/blob/f2dc1d7b7223d1471fa29c871911025246425bac/project/polls/views.py#L81-L90

Now the server does not experience an error and an appropriate HTML status code is shown to the user:

_url-link-to-screenshot_
