# Steps to get started developing

## 1. Download Python (if you haven't already)

To check that this is done, go to your command line and type

`
$ python --version
`

and it should respond with your current version of python.

## 2. Set up SSH keys with Github (if you haven't already)

## 3. Clone the repository

## 4. Create and activate the virtual environment

`
$ python -m venv .venv
$ .venv/Scripts/Activate.ps1
`

## 5. Install requirements

`
$ python -m pip install -r requirements.txt
`

## 6. Initialize database

`
$ python manage.py migrate
`

## 7. Run the project

`
$ python manage.py runserver
`