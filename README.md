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