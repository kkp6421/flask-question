# flask-question

This application worked on docker-compose ans wsgi.
if you want to start this application, you have to do 4 steps.

1 ```docker-compose build```

2 ```docker-compose run web python manage.py db init```

3 ```docker-compose run web python manage.py db migrate```

4 ```docker-compose up```
