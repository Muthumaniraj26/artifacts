FROM python:3.10.18

WORKDIR /code

COPY ./requirement_fast.txt /code/requirement_fast.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirement_fast.txt

COPY ./app /code/app
COPY ./static /code/static    
COPY ./templates /code/templates  

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

