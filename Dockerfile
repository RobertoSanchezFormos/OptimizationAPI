FROM python:3.8
ADD requirements.txt .
RUN pip3 install -r requirements.txt
WORKDIR .
ADD /app /app
ADD /app_prod.py /app_prod.py
ADD /app_dev.py /app_dev.py
ADD /run_app.py /run_app.py

# ports to expose:
EXPOSE 8000

# main program:
CMD ["python3", "./app_prod.py"]