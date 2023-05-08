# Exact wrapper
Used to interact with the ExactOnline API to automate contracts

## Getting started
- Use Python3.11+ and execute these commands from the main directory:
  - `python -m venv .venv`
  - `. .venv/bin/activate` (for Windows: `.venv\Scripts\activate`)
  - `pip install poetry`
  - `poetry install`
- Make sure to have a Mongo database somewhere
  - For example, install a client and run a database locally
- Create a `.env` file in the main directory
  - See `config.py` for the necessary variables
- Run the app:
  - `python src/main.py`

## Users
- This API makes use of a MongoDB with users and beanie as ODM.
- Authentication transport mode is cookie (as we'll be creating a web frontend) (fastapi-users also supports JWT)
- Authentication strategy is OAuth (but fastapi-users provides JWT/Database/Redis?)