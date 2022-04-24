# rest-web-service

## Run server:
```
docker-compose up --build --scale worker=2 rabbitmq worker server
```

## Run example client:
```
pip3 install -r example/requirements.txt
python3 example/client.py
```

Generated pdf: `example/report.pdf`
