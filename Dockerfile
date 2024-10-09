FROM continuumio/miniconda3:4.11.0

SHELL ["/bin/bash", "-c"]
RUN conda install geopandas==0.14.2
ENV PROJ_LIB=/opt/conda/share/proj

RUN mkdir -p /home/app

WORKDIR /home/app

COPY requirements.txt ./

RUN conda install -c conda-forge --file requirements.txt

COPY data data/

COPY src src/

WORKDIR /home/app/src

EXPOSE 8501

CMD ["streamlit","run","main.py","--server.address=0.0.0.0","--server.port=8501"]