*[This Project is a Work in Progress]*
# Analysis of Boston Airbnb data

### 2025-10-06 Progress Update
- Switched to PostgreSQL from MySQL
- Added Docker Compose to have Postgres run in a container

### Instructions to run the code:
- Install Docker Desktop (https://www.docker.com/products/docker-desktop/)
- (Optional) Install Python (https://www.python.org/downloads/release/python-31011/). Only if you want to run the scripts outside Docker.
- Create a `.env` file with the required credentials to connect to the database. The `.env` file must have the Username, Password and Database Name. Example of the `.env` file:
```
user=exampleairbnbuser
password=examplepassword123
db_name=airbnbdatabase
```
- Open Command Prompt or Terminal (Or a prefered code editor)
- In the terminal run the following command: `docker-compose up -d --build`. This will build the docker images and start the containers. `-d` makes it run in detached mode. If you want to have the logs stream to your terminal run: `docker-compose up --build` instead.
- Open http://localhost:8501 in your browser to view the streamlit app.
- To close the containers run: `docker-compose down`. If you want to also remove the volumes (resets the database) run: `docker-compose down -v`. 
- For subsequent runs you can just run: `docker-compose up` to not have to rebuild the images each time if you haven't changed anything.


### Source for the Dataset
https://insideairbnb.com
