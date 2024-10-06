FROM continuumio/miniconda3:4.11.0

RUN mkdir -p /home/app

COPY data /home/app

COPY src /home/app

COPY requirements.txt /home/app

EXPOSE 8501

RUN conda install -c conda-forge --file /home/app/requirements.txt

CMD ["streamlit","run","/home/app/main.py","--server.address=0.0.0.0","--server.port=8501"]