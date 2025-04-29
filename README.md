# Instructions/How to Run
To run the MySQL docker container, run
```bash
docker-compose up -d # the -d runs it in detached mode
```

To stop the container, run
```bash
docker-compose down
# OR
docker-compose down -v # the -v will remove the named volumes (wipe data)
```

To access MySQL, we can do one of the following:
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p # from the host
```
OR
```bash
sudo docker exec -it mysql-db mysql -u root -p  
```

# Python Notes:
Before Python 3, we used to need `__init__.py` for defining a package, but this is no longer needed (though it is recommended).

Python automatically includes the root directory of the project into sys.path, which is how it detects packages/modules (also includes other libraries/pip packages).

That's why we can use
```python
from app import models
from app.db import engine
```
as Python treats app as a top level package.

## Running python as a script
Running 
```python
python app/main.py
```
is running a program like a script. The file is assigned 
```python
__name__ == "__main__"
```
sys.path[0] becomes the directory containing the script, i.e. app/.
Imports are relative to that path — app is NOT on sys.path, so this fails:
```python
from app import models  # ImportError
```
## Running python as a module
Running
```python
python -m app/main.py
```
is running a program like a module. Python runs main.py as part of the app package. The file is still assigned:
```python
__name__ == "__main__"
```
However, sys.path[0] becomes the directory containing the app/ folder, i.e. your project root.
app is now a top-level package, so:
```python
from app import models  # Works
from . import db        # Relative import also works
```