FROM python:3.12

WORKDIR /ETL-VALSA

RUN apt-get update \
    && apt-get install -y \
        unixodbc-dev \
        unixodbc \
        freetds-dev \
        freetds-bin \
        tdsodbc \
        libpq-dev \
        gcc \
        python3-psycopg2 \
        git \
        vim \
        build-essential

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
RUN pip3 install streamlit
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
