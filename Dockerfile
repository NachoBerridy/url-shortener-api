FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# Ver archivos en source
#CMD ls -la source
#RUN echo "-------------------"
# ls -la dest
#RUN echo "-------------------"
#RUN ls -la

CMD ["uvicorn", "source.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]