FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV DB_HOST=host.docker.internal
ENV DB_DATABASE=roomr
ENV DB_USER=root
ENV DB_PASS=root
ENV PORT=$PORT

COPY . .

#CMD ["python", "./main.py"]
CMD uvicorn main:app --host 0.0.0.0 --port $PORT

