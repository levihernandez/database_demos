# DB Migration Setup

* Database Docker Compose/Local install:
  * MySQL `sudo docker pull mysql:8.0`
    * `cd docker-compose/cockroachdb; docker compose up -d`
    * `export PYTHONPATH=$PYTHONPATH:/path/to/mysql-connector-python`
  * MSSQL `sudo docker pull mcr.microsoft.com/mssql/server:2022-latest`
  * CockroachDB `sudo docker pull cockroachdb/cockroach:v23.1.1`
    * `cd docker-compose/cockroachdb; docker compose up -d`
    * Find the container name: `docker compose ps`
    * Initialize the cluster: `docker exec -it cockroachdb-roach-01-1 ./cockroach init --insecure --host=roach-01`
    * Connect to the SQL Console:
      `cockroach sql --insecure --url "postgres://root@localhost:26257/defaultdb?sslmode=disable"`
* Install Python Packages
  * Packages `pip install streamlit Faker mysql-connector-python pandas psycopg2 psutil cockroachdb urllib3==1.24.3`
  * Optionally run: `pip install -r requirements.txt -v`
* Streamlit
  * Set streamlit path if needed: `export PYTHONPATH=$PYTHONPATH:/Users/jlhernandez/Workbench/Projects/gogs/db_migration/venv/bin/streamlit`
  * Run Streamlit: `cd ../../; streamlit run Home.py`
