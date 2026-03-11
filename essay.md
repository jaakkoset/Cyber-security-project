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

Start the application:

    (virtual-env) $ python3 manage.py runserver

The example data adds two users (username:password):

    bob:squarepants
    alice:redqueen

FLAW 1. CSRF attack.

The flaw is in the save_poll route function:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L74

The save_poll route function is vulnerable to CSRF attacks. If a user is logged-in and he visits a malicious website, that site can add polls without the users knowledge. This is possible because save_poll does not have any CSRF checks.

To demonstrate the attack, log in at http://localhost:8000/polls/. In a new terminal window, go to the csrf/ directory and run

    python3 -m http.server 9000

Then, in a new browser tab, open this page:

    http://localhost:9000/csrf.html

Reloading http://localhost:8000/polls/ will now reveal that a new malicious poll has been added.

The vulnerability is easily fixed by changing the save_poll function to use POST requests. Django automatically checks the CSRF token with POST requests. Lines 72 and 102-108 in save_poll have the fixed code commented out:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L72

https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L102-L108

Also, the corresponding html form should be modified to send POST requests:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/templates/polls/create.html#L23

FLAW 2. Voting without logging in.

The source of the flaw is in the vote route function:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L43

Voting should be possible only to users. The voting functionality is hidden from others in the UI, but by sending a POST request to the right address anyone can still vote. This flaw belongs to the OWASP A01 Broken access control -category.

The vulnerability can be demonstrated by running the following code in a browser console (as shown in screenshot
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw2-before-browser_before_refreshing.png):

var csrf_token = document.cookie.match(/csrftoken=([^;]+)/)[1]

fetch("/polls/6/vote/", {
method: "POST",
headers: {
"Content-Type": "application/x-www-form-urlencoded",
"X-CSRFToken": csrf_token
},
body: "choice=15"
})

The problem can be fixed using Django’s @login_required-decorator. This ensures that only logged in users can send requests to the route function. The one-line-fix is commented out here:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L43

FLAW 3. SQL injection

Source of the problem is in the save_question function in database.py:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L30-L37

When creating a new poll, it is possible to inject SQL code into the question field. For example, injecting the following code results in two polls being created, one which has no choices and another which has no question, making it unclickable at the front page:

    No choices LOL", CURRENT_TIMESTAMP), ("", CURRENT_TIMESTAMP) --

The injection is illustrated in screenshot
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-before-injection.png
and the result is shown in screenshot
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-before-result.png

This problem belongs to the OWASP A05 Injection -category.

The problem can be fixed by sanitizing inputs. This is easy to do with sqlite’s parameter binding. The fixed code is commented out at lines 40-48:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L40-L48

After the fix, the input is treated as text and not as SQL code. This is illustrated in the screenshot https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw3-after.png

FLAW 4. Outdated dependency

The version of Django is set in the requirements.txt file:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/requirements.txt#L2
The version can also be checked from terminal:
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw4-before.png

The project uses the Django version 5.1.15, which is unsupported as is listed here:
https://www.djangoproject.com/download/
This problem belongs to the OWASP A06 Outdated component -category.

To fix the problem one should upgrade Django to a supported version. In this case it is possible to upgrade to the latest version without breaking anything. To upgrade use this command:

    (virtual-env) $ pip install --upgrade django

Here is a view of the terminal after doing that:
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw4-after.png

FLAW 5. Mishandling of exceptional conditions

User can create a poll that has no choices, as shown in screenshot https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw5-before-poll.png
This can happen when the user modifies the url by removing choices. For example like this:
http://localhost:8000/polls/save-poll/?question=How much do you sleep?&choice1=less than 8 hours.&choice2=at least 8 hours
The given url is missing choice3 and choice4. The application expects empty strings for missing
choices, but when they are omitted entirely, the code raises an error when trying to access those keys in the request dictionary. The error happens at this line, where “choice3” and “choice4” are hard-coded:
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L14

Critically, the error happens after the question has been added to the database, but before the choices for the question have been added. This is why a poll without choices is created. This problem belongs to the OWASP A10 Mishandling of Exceptional Conditions -category.

There are to fixes to the problem. The first fix is to make sure that the question and choices are committed to the database at the same time. This is done by uncommenting the line
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L21
and removing lines
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L50
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/database.py#L67
This way either both the question and choices are save to the database or, if something goes wrong, nothing is.

That still causes an error however. To prevent that from happening, a commented out fix is added at lines
https://github.com/jaakkoset/Cyber-security-project/blob/master/project/polls/views.py#L78-L87
The code checks that the request data has everything as exepcted. If something is missing, an error is displayed to the user, as shown in this sreenshot:
https://github.com/jaakkoset/Cyber-security-project/blob/master/screenshots/flaw5-after.png
