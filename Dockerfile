FROM python:3.12

RUN apt-get update
RUN apt-get -y install locales locales-all
RUN locale-gen nb_NO.UTF-8

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
RUN pip install --no-cache-dir --upgrade /code

COPY ./handlelistesystem /code/handlelistesystem

EXPOSE 80

CMD ["fastapi", "run", "handlelistesystem/main.py", "--port", "80", "--workers", "4"]