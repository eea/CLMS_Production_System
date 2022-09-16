FROM continuumio/miniconda3

LABEL MAINTAINER="Johannes Schmid"

ENV PYTHONDONTWRITEBYTECODE=true
ENV PROJ_LIB=/opt/conda/share/proj

RUN conda config --append channels conda-forge \
    && conda install -y \
       git \
       pip \
       nomkl \
       GDAL \
       pandas \
       rasterio \
       geopandas \
       pika \
       cryptography \
       dask \
    && git clone https://clcbb:g8phxTCpTDwsUVAftQTN@gitlab.clcplusbackbone.geoville.com/system_modules/python/clcplus_storage_gate.git \
    && cd clcplus_storage_gate/geoville_ms_storage_gate_modul \
    && pip install -e . \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && /opt/conda/bin/conda clean -afy

ENV PATH=/opt/conda/bin:$PATH

# Sets current working directory
WORKDIR /code

# Copies the application code to the current working directory
COPY product_netcdf_upload.py /code

