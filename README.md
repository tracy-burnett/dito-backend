# Xygil Backend

## Setup

### Prerequisites
- Python 3
- Pip
- PostgreSQL
- MySQL
Note: We are going to be working with MySQL for familiarity, but Heroku uses PostgreSQL. Having PostgreSQL means that our app can automatically migrate our MySQL database to Heroku's PostgreSQL database on deploy.

**Configure MySQL**

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


Modify `my.cnf` (usually in `/etc/mysql/my.cnf` for Linux and `/usr/local/etc/my.cnf` for Mac) to the following, again replacing `<password>` with your previously chosen password:
```
...
[client]
database = xygil
user = xygil
password = <password>
default-character-set = utf8

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