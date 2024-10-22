# URL Shortener API

Acortador de URLs con gestión de usuarios y API RESTful. Desarrollado con FastAPI y PostgreSQL. Este repositorio corresponde al backend del proyecto. ([frontend](https://github.com/NachoBerridy/url-shortener-client))

## Tech Stack:
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?logo=docker&logoColor=white)
![Alembic](https://img.shields.io/badge/-Alembic-ffffff?logo=alembic&logoColor=black)

## Características principales

- Acortamiento de URLs
- Gestión de usuarios
- API RESTful
- Uso de dos bases de datos separadas para URLs y usuarios

## Arquitectura

El siguiente diagrama muestra la arquitectura cliente-servidor de nuestro sistema:

```mermaid
graph TD;
    A[Cliente] -->|HTTP Requests| B[Servidor FastAPI];
    B -->|Gestión de URLs| C[(Base de datos URLs)];
    B -->|Gestión de Usuarios| D[(Base de datos Usuarios)];
    B -->|HTTP Responses| A;
```

### Explicación del diagrama

- El cliente envía solicitudes HTTP al servidor.
- El servidor FastAPI procesa estas solicitudes y realiza operaciones en las bases de datos según sea necesario.
- Hay dos bases de datos separadas:
  1. Base de datos de URLs: Almacena las URLs originales y sus versiones acortadas.
  2. Base de datos de Usuarios: Almacena la información de los usuarios registrados.
- El servidor envía respuestas HTTP de vuelta al cliente.

## Guía de instalación

### Requisitos previos

- Docker
- Docker Compose
- python3
- pip3

### Pasos

1. Configurar las variables de entorno en un archivo `.env` en la raíz del proyecto. Puedes usar el archivo `.env.example` como referencia.

2. Construir y levantar los contenedores de Docker:


```bash
docker-compose up --build
```


