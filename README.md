# Xygil Backend

As of 2/21/2022, main branch code auto-deploys to api.xygil.net.  But only skysnolimit08 has the ability to run migrations on the database it communicates with.

## Setup updated 3/7/2022
(Note: I removed the mysqlclient package from Pipfile because it did not seem necessary and was causing problems for setup on Macs.  Please let me know if this causes any problems down the line.)

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
            "description": "War and Peace",
            "public": true
        },
        {
            "url": "aws.amazon.com/cloudfront/12395323",
            "title": "Audio2",
            "id": 2,
            "description": "Gettysberg Address",
            "public": false
        },
    ]
}
```

# Audio
Create, read, update, and delete audio.

## Create Audio
Working on 4/26/2022.  

**URL** : `/storybooks/audio/`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "id": "1",
    "url": "aws.amazon.com/cloudfront/1249513",
    "title": "A random audio file",
    "description": "a description",
    "archived": false,
    "uploaded_at": "2022-04-26T06:29:06.159347Z",
    "uploaded_by": 1,
    "last_updated_at": "2022-04-26T06:29:06.159356Z",
    "last_updated_by": 1,
    "shared_with": [
        1,
        2
    ],
    "public": false,
    "id_token": "randomToken"
}
```
## Read Public Audio
Returns a list of public, non- archived audio files.\
**URL** : `/storybooks/audio/`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "audio": [
        {
            "title": "Audio 3",
            "id": "3",
            "description": "A description",
            "url": "aws.amazon.com/cloudfront/12395324"
        },
        {
            "title": "Audio 2",
            "id": "2",
            "description": "A description",
            "url": "aws.amazon.com/cloudfront/12395325"
        },
        {
            "title": "Audio",
            "id": "5",
            "description": "A description",
            "url": "aws.amazon.com/cloudfront/12395326"
        }
    ]
}
```

## Read Public Audio for a User
Returns a list of public, non- archived audio files for a specific user.\
**URL** : `/storybooks/audio/user/<int:uid>`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "audio": [
        {
            "title": "Audio 1",
            "id": "3",
            "description": "A description",
            "url": "aws.amazon.com/cloudfront/123953124"
        },
        {
            "title": "Audio",
            "id": "5",
            "description": "A description",
            "url": "aws.amazon.com/cloudfront/12313"
        }
    ]
}
```

## Read Private Audio for a User
Returns a list of audio files that a user created, or (which have been shared with them and  not archived).\
**URL** : `/storybooks/audio/user/`

**Method** : `GET`

**Auth required** : No

**Content example**

```json
{
    "audio": [
        {
            "id": "1",
            "url": "google.com",
            "title": "A random audio file",
            "description": "a description",
            "archived": false,
            "uploaded_at": "2022-04-26T06:29:06.159347Z",
            "uploaded_by": 1,
            "last_updated_at": "2022-04-26T06:29:06.159356Z",
            "last_updated_by": 1,
            "shared_with": [
                1,
                2
            ],
            "public": false
        },
        {
            "id": "1",
            "url": "google.com",
            "title": "A random audio file",
            "description": "a description",
            "archived": false,
            "uploaded_at": "2022-04-26T06:29:06.159347Z",
            "uploaded_by": 1,
            "last_updated_at": "2022-04-26T06:29:06.159356Z",
            "last_updated_by": 1,
            "shared_with": [
                1,
                2
            ],
            "public": false
        }
    ]
}
```

## Update Audio as an editor
A logged-in user can update some fields of audio entries that have been shared with them and not archived. Working as of 4/26/2022.

**URL** : `/storybooks/audio/<int:audio_id>/editor`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "title": "A new title",
    "description": "Twenty-seven minutes of people coughing",
}
```

## Update Audio as an owner
A logged-in user can update most fields of audio entries they created. Working as of 4/26/2022.

**URL** : `/storybooks/audio/<int:audio_id>/owner`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "title": "A new title owner",
    "description": "Making the audio public since I'm an owner",
    "public": true
}
```



## Delete Audio
Working on 3/7/2022.  Authentication not tested.

**URL** : `/audio/:id`

**Method** : `DELETE`

**Auth required** : Yes



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
