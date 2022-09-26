# ChoreMinder

An app to keep track of chores that need to be completed periodically.

## Development

### Option 1: Use VSCode

Prequisites:
- [VSCode](https://code.visualstudio.com/)
- [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Clone the project and open it in the container. All of the needed extensions and python dependencies should be
automatically installed. Once it finishes, open the shell and run the following commands:

```
python manage.py migrate
python manage.py runserver
```

### Option 2: Use pipenv

Prequisites:
- [Python 3.10](https://www.python.org/downloads/release/python-3107/)
- [pipenv](https://pipenv.pypa.io/en/latest/)

Clone the project, navigate into it in the terminal, and run the following commands:

```
pipenv install --dev
pipenv shell
python manage.py migrate
python manage.py runserver
```

### Create a new migration

After making updates to the model classes, create a migration using the following command:

```
python manage.py makemigrations chores
```

### Running tests

```
python manage.py test chores
```
