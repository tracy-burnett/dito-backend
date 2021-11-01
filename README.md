# Xygil Backend

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