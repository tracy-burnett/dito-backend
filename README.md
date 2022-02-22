# Xygil Backend

## As of 2/21/2022, main branch code auto-deploys to api.xygil.net.  But only skysnolimit08 has the ability to run migrations on the database it communicates with.

## Setup

### Prerequisites
- Python 3
- Pip
- PostgreSQL/MySQL/SQLite

**Configuring Environmental Variables**

Edit `.env` based on your environment:
```
SECRET_KEY=SECRET_KEY
DEBUG=False
DATABASE_URL=mysql://xygil:<password>@localhost:3306/xygil
```
Set `DEBUG=True` locally for more verbose console logging. Set `DATABASE_URL` to be the database url of whatever database service you use. The format shown is for MySQL, but adjust accordingly.

**Configuring MySQL**

Create new database and user with the following queries. Make sure to replace `<password>` with your desired password. This user can also be used to access the database manually through the MySQL console.
```
$ sudo mysql -u root

mysql> CREATE DATABASE xygil;
Query OK, 1 row affected (0.00 sec)

mysql> CREATE USER 'xygil'@'%' IDENTIFIED WITH mysql_native_password BY '<password>';
Query OK, 0 row affected (0.00 sec)

mysql> GRANT ALL ON xygil.* TO 'xygil'@'%';
Query OK, 0 row affected (0.00 sec)

mysql> FLUSH PRIVILEGES;
Query OK, 0 row affected (0.00 sec)
```

Restart the MySQL service with `brew services restart mysql` (Mac) or `sudo systemctl restart mysql` (Linux)


**Installing Dependencies**
```
$ git clone https://github.com/skysnolimit08/dialecttranslationtool-backend backend
$ cd backend
$ pip install pipenv
$ pipenv install
```

**Connecting MySQL with Django**

In the same project directory:
```
$ pipenv shell
(venv) $ python manage.py migrate
```

## Running the Server
```
$ pipenv shell
(venv) $ python manage.py runserver # Defaults to http://localhost:8000
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

**URL** : `/user/:id`

**Method** : `DELETE`

**Auth required** : Admin

## Index User Audios

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

**URL** : `/audio/`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "url": "aws.amazon.com/cloudfront/123456789",
    "title": "Audio1",
    "description": "Thirty minutes of people coughing",
    "public": false
}
```
## Read Audio
Returns the link, name, description of an audio if public.\
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

**URL** : `/audio/:id`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "description": "Twenty-seven minutes of people coughing",
    "public": true
}
```

## Delete Audio

**URL** : `/audio/:id`

**Method** : `DELETE`

**Auth required** : Yes

## Index Audios
Returns a list of all public audios.\
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
Returns the translation with language `:lid` of an audio `:id`.\
**URL** : `/audio/:id/translations/:lid`

**Method** : `POST`

**Auth required** : Yes

**Data example**

```json
{
    "user": "user1", 
    "text": "Four score and seven years ago, our fathers brought forth on this continent...",
    "lid": 5,
    "public": false
}
```
## Read Translation
Returns entire translation if public or authenthenticated and private.\
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
Updates the entire text. This operation will automatically maintain existing associations for words that aren't deleted and insert NULL associations for newly inserted words. \
**URL** : `/audio/:id/translations/:lid`

**Method** : `PATCH`

**Auth required** : Yes

**Data example**

```json
{
    "text": "Eighty-seven years ago, our fathers brought forth on this continent...",
}
```

## Delete Translation

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
