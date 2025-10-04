*[This Project is a Work in Progress]*
# Analysis of Boston Airbnb data

### 2025-10-03 Progress Update
- Created a streamlit based frontend to run the Pipeline

### Instructions to run the code:
- Open Command Prompt or Terminal (Or a prefered code editor)
- (Optional) Create a virtual environment: `python -m venv .venv`. To activate it: `.venv\Scripts\activate` for Windows or `source .venv/bin/activate` for macOS and Linux. (Creating a virtual environment is strongly recommended to install packages into)
- Install required packages using: `pip install -r requirements.txt`
- Ensure you have a mySQL server instance up and running (Check out https://dev.mysql.com/doc/mysql-getting-started/en/ for more info)
- Create a `.env` file in the `utilities` folder with the required credentials to connect to the database. The `.env` file must have the Username, Password and Database Name. Example of the `.env` file:
```
user = exampleairbnbuser
password = examplepassword123
db_name = airbnbdatabase
```
- To get the files, run `datascraper.py` using the command: `python utilities/datascraper.py`
- To preprocess the files for database loading, run `datapreprocessor.py` using the command: `python utilities/datascraper.py`
- To load the files into the database (and create the required tables), run `dbcreator.py` using the command: `python utilities/dbcreator.py`

### Source for the Dataset
https://insideairbnb.com
