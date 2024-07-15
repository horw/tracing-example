Run docker-compose
```bash
docker-compose up
```

Run service 1
```bash
SERVICE_NAME=service-1 fastapi run app.py --port 8080 # call POST /chain in this service
```

Run service 2
```bash
SERVICE_NAME=service-2 fastapi run app.py --port 8081
```

Run service 3
```bash
SERVICE_NAME=service-3 fastapi run app.py --port 8079
```
