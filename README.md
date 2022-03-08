# Xygil Backend

As of 2/21/2022, main branch code auto-deploys to api.xygil.net.  But only skysnolimit08 has the ability to run migrations on the database it communicates with.

## Setup updated 3/7/2022

### Prerequisites

- Git
- Python 3
- Pip

You can check if you have these by typing

(Windows)
```
$ git --version
$ python --version
$ pip --version
```

(Mac)
```
$ git --version
$ python3 --version
$ pip3 --version
```

- If you don't have Git, download it from git-scm.com/downloads/
- If you don't have Python 3, you can download it from https://www.python.org/downloads/
- - on Windows if you install this, you will want to check the box for "add Python to PATH", or else you will have to retroactively do it manually or do it by modifying the install.
- Pip or Pip 3 will install automatically when you install Python 3, which is great (unless you somehow prevent it, which you shouldn't).

**Installing Dependencies**

In your terminal, change directories into the folder you want to keep the project in.  Then:

Windows
```
$ git clone https://github.com/skysnolimit08/dialecttranslationtool-backend backend
$ cd backend
$ pip install pipenv
$ pipenv install
```

Mac
```
$ git clone https://github.com/skysnolimit08/dialecttranslationtool-backend backend
$ cd backend
$ pip3 install pipenv
$ pipenv install
```

(The pip command will work on Windows; the pip3 command will work on Mac)

From now on, if you install a new package for the project, please do so using the command 'pipenv install package-name' from that same backend folder so that the Pipfile keeps track of what package dependencies our project needs for future developers and hosting servers.


**Configuring Environmental Variables**

Rename ".env-example" to ".env".  Paste the following code into it.  Create your own randomized value for SECRET_KEY.  You can use python secrets to help you do that.  Setting debug to True in your local environment will be helpful for debugging your code.  You probably do not need to use the DATABASE_URL environmental variable, since our settings.py file includes a default database URL, but you are welcome to if you want to host your database in a special place.

```
SECRET_KEY='SECRET_KEY'
DEBUG_VALUE='True'
# DATABASE_URL=mysql://xygil:<password>@localhost:3306/xygil
```
Now, restart your terminal.


**Connecting MySQL with Django**


Windows
```
$ cd backend
$ pipenv shell
(venv) $ python manage.py migrate
```
Mac
```
$ cd backend
$ pipenv shell
(venv) $ python3 manage.py migrate
```

**Configuring an administrative "superuser" for MySQL**

Windows
```
$ pipenv shell
(venv) $ python manage.py createsuperuser
Username: 
Email address: 
Password: 
Password (again):
```
Mac
```
$ pipenv shell
(venv) $ python3 manage.py createsuperuser
Username: 
Email address: 
Password: 
Password (again):
```


## Running the Server
Windows
```
$ pipenv shell
(venv) $ python manage.py runserver # Defaults to http://localhost:8000
```
Mac
```
$ pipenv shell
(venv) $ python3 manage.py runserver # Defaults to http://localhost:8000
```
Now, navigate to http://localhost:8000 and you should see the server running!

# Models
## `Audio`
```python
class Audio:
    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"

    url             = CharField(max_length=255)
    title           = CharField(default="Untitled", max_length=255)
    archived        = BooleanField(default=False)

    # Metadata
    createdAt       = DateTimeField()
    updatedAt       = DateTimeField()
    lastUpdatedBy   = ForeignKey(User, null=True, on_delete=SET_NULL)
```
## `Translation`
```python
class Translation:
    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"

    title           = CharField(max_length=255)
    audio           = ForeignKey(Audio, on_delete=CASCADE)
    published       = BooleanField(default=False)

    # Metadata
    author          = ForeignKey(User, null=True, on_delete=SET_NULL)
    createdAt       = DateTimeField()
    updatedAt       = DateTimeField()
    lastUpdatedBy   = ForeignKey(User, null=True, on_delete=SET_NULL)
```
## `Story`
```python
class Story:
    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"

    translation     = ForeignKey(Translation, null=True, on_delete=SET_NULL)
```


## Xygil API

# Users
Create, read, update, and delete user.

## Create User
Working 3/7/2022.  Did not test authentication.  Is not safe and code needs to be deprecated and replaced with Django Auth functions.

**URL** : `/user/`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "username": "user1",
    "name": "Xygil Net",
    "email": "example@xygil.net",
    "password": "xygil123",
    "description": "A dude"
}
```
## Read User
Working 3/7/2022.

**URL** : `/user/:id`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "email": "example@xygil.net",
    "name": "Xygil Net",
    "description": "A dude"
}
```

## Update User
Is probably not safe and code needs to be deprecated and replaced with Django Auth functions.

**URL** : `/user/:id`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "email": "example@xygil.net",
    "password": "xygilxygil123"
}
```

## Delete User
May not be safe to the point that code needs to be deprecated and replaced with Django Auth functions.

**URL** : `/user/:id`

**Method** : `DELETE`

**Auth required** : Admin

## Index User Audios
3/7/2022 Can't get this to work, and not sure where to find the code for it in the backend.

**URL** : `/user/:id/audio`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "num": 2,
    "audio": [
        {
            "url": "aws.amazon.com/cloudfront/136523",
            "title": "Audio1",
            "id": 1,
            "description": "War and Peace"
            "public": true
        },
        {
            "url": "aws.amazon.com/cloudfront/12395323",
            "title": "Audio2",
            "id": 2,
            "description": "Gettysberg Address"
            "public": false
        },
    ]
}
```

# Audio
Create, read, update, and delete audio.

## Create Audio
Working on 3/7/2022.  Authentication not tested.

**URL** : `/audio/`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "url": "aws.amazon.com/cloudfront/123456789",
    "title": "Audio1",
    "description": "Thirty minutes of people coughing",
}
```
## Read Audio
Returns the link, name, description of an audio if public.  Working on 3/7/2022.  Authentication not tested.\
**URL** : `/audio/:id`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "url": "aws.amazon.com/cloudfront/123456789",
    "title": "Audio1",
    "description": "Thirty minutes of people coughing"
}
```

## Update Audio
As of 3/7/2022, it works.

**URL** : `/audio/:id/`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "description": "Twenty-seven minutes of people coughing",
}
```

## Delete Audio
Working on 3/7/2022.  Authentication not tested.

**URL** : `/audio/:id`

**Method** : `DELETE`

**Auth required** : Yes

## Index Audios
Returns a list of all public audios.  3/7/2022 doesn't seem to work, probably because there is no "public" field in audio table.\
**URL** : `/user/:id/audio`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "audio": [
        {
            "url": "aws.amazon.com/cloudfront/2151232",
            "title": "Audio1",
            "id": 1,
            "description": "War and Peace"
        }
    ]
}
```

# Translations
Create, read, update, and delete translations associated with an audio.

## Create Translation
Creates translation object.  Returns the translation with language `:lid` of an audio `:id`.  3/7/2022 For this to work, need to comment out the Check unique section of views.py.  But then that breaks some other things down the line.\
**URL** : `/audio/:id/translations/:lid`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "user": "user1", 
    "title": "test title",
    "text": "Four score and seven years ago, our fathers brought forth on this continent...",
    "lid": 5,
    "public": false
}
```
## Read Translation
Returns entire translation if public or authenticated and private.  Working as of 3/7/2022.  Did not test authentication.\
**URL** : `/audio/:id/translations/:lid`

**Method** : `GET`

**Auth required** : Yes/No

**Content example**

```json
{
    "text": "Four score and seven years ago, our fathers brought forth on this continent...",
}
```

## Update Translation
Updates the entire text. This operation will automatically maintain existing associations for words that aren't deleted and insert NULL associations for newly inserted words.  Working as of 3/7/2022. Did not test authentication.\
**URL** : `/audio/:id/translations/:lid/`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "text": "Eighty-seven years ago, our fathers brought forth on this continent..."
}
```

## Delete Translation
Works 3/7/2022.  But doesn't delete or archive the associated stories.

**URL** : `/audio/:id/translations/:lid`

**Method** : `DELETE`

**Auth required** : Yes

## Index Translation Languages
Returns a list of all available public languages for the translation.\
**URL** : `/audio/:id/translations`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "languages": [0, 1, 3, 5, 6]
}
```

# Languages

## LanguageID to Language

**URL** : `/languages`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    0: "English",
    1: "Spanish",
    2: "Chinese"
}
```

# Associations

## Get Associations for Highlighting
Returns the text between `ts1` and `ts2` along with a dictionary which maps sorted timestamp intervals to highlighted portions of text. Ex. From 0 to 3000 ms, characters between character index 0-9 and 16-20 (inclusive) should be highlighted (Four score/seven). From 3500 to 5000 ms, character from index 11-15 should be highlighted (and). If there are no configured associations, returns the entire text.\
**URL** :  `/audio/:id/translations/:lid/associations?ts1=int&ts2=int`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "text": "Four score and seven years ago, our fathers brought forth on this continent...",
    "associations": {
        "0-3000": ["0-9", "15-19"],
        "3500-5000": ["11-13"]        
    }
}
```
## Update Associations
Given a portion of the text, associates particular indexes with timestamps(ms). The specific way how this works is the first portion of exclusive text matching this substring will be updated which is not ideal (since there may be infrequent cases of unintended associations if the "text" is too short) but simplifies the work done front end and the amount of text metadata needed immensely.\
**URL** :  `/audio/:id/translations/:lid/associations`

**Method** : `POST`

**Auth required** : Yes

**Content example**

```json
{
    "text": "seven years ago, our fathers brought forth on this continent",
    "associations": {
        15: 2400,
        23: 1500,
        34: 3567
    }
}
```
