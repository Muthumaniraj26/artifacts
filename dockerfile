<<<<<<< HEAD
FROM python:3.10.18

WORKDIR /code

COPY ./requirement_fast.txt /code/requirement_fast.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirement_fast.txt

COPY ./app /code/app
COPY ./static /code/static    
COPY ./templates /code/templates  

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

=======
FROM python:3.10.18

WORKDIR /code

# Copy requirements and install
COPY ./requirement_fast.txt /code/requirement_fast.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirement_fast.txt

# Copy app files
COPY ./app.py /code/app.py
COPY ./static /code/static
COPY ./templates /code/templates
COPY ./artifact_with_val.pth /code/artifact_with_val.pth


EXPOSE 5000

CMD ["python", "app.py"]
>>>>>>> 0bd2f86 (Initial commit for Flask artifact app)
