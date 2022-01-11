# Warbler

Back-end for [Warbler](https://warbler-klin.herokuapp.com), a twitter-like social network web application.

## Completed Features
- Login/Signup
- User can: 
    - view profiles
    - follow other users
    - create public messages
    - like messages

## Getting Up & Running
1. Flask Environment Setup
    ```console
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    ```
2. Database Setup
    ```console
    (venv) $ psql
    =# CREATE DATABASE warbler;
    =# (control-d)
    (venv) $ python seed.py
    ```
3. .env File Setup

    Add the following lines to your .env file:
    ```txt
    SECRET_KEY=fake_key
    DATABASE_URL=postgresql:///warbler
    ```
4. Run the Server
    ```console
    (venv) $ flask run
    ```
## More to-dos:
- Sending direct messages
- Allow admin users
