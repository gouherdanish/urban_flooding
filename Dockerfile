FROM continuumio/miniconda3:4.11.3

RUN mkdir -p /home/app

COPY data /home/app

COPY src /home/app

COPY requirements.txt /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["streamlit","run","main.py"]