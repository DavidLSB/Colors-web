# Colors-web
School project: a website made with Flask, SQL, HTML, CSS, JavaScript, Docker, Bootstrap and Psycopg2.

Colors is a web that allows the user to save, erase, and mix Colors. Each color is saved in a card, in which information about it (such as complementary colors) can be added.

How to run:
Enter the docker container with -it
If you dont have a db running, you can do it with something like:
docker run --name colorsdb_docker -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=colorsdb -p 5432:5432 -d postgres
docker exec -it colorsdb_docker bash

Run the container with -p 5000:5000
Run in the container:
. venv/bin/activate
cd BackEnd
python
from app import db
db.create_all()
exit()
flask run --host=0.0.0.0 --debug
