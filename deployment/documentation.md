# Web Server & Proxy Architecture

## Overview

This Django boilerplate API uses a multi-layered proxy setup involving:
1. A host Nginx server (running on the host machine)
2. A containerized Nginx server (running in Docker)
3. A Django application server (running in Docker)

This architecture provides security, efficient static file serving, and proper routing of requests.

## Architecture Diagram

```
Client Request → Host Nginx (SSL termination) → Docker Nginx → Django Application
                                              ↓
                         Serves static/media files directly when applicable
```

## Components

### 1. Host Nginx Server

This is the entry point for all HTTP requests from clients, running on the host machine.

```nginx
server {
    server_name your-domain.com;

    # Increase maximum upload size
    client_max_body_size 10M;

    # Proxy everything else to the Docker Nginx container
    location / {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Add this to prevent redirects due to trailing slashes
        proxy_redirect off;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = your-domain.com) {
        return 301 https://$host$request_uri;
    }

    server_name your-domain.com;
    listen 80;
    return 404;
}
```

**Key responsibilities:**
- SSL termination (HTTPS handling)
- HTTP to HTTPS redirection
- Setting a reasonable upload size limit
- Forwarding requests to the Docker Nginx container on port 8081
- Passing necessary headers for proper proxy operation

### 2. Docker Nginx Container

This Nginx instance runs inside Docker and handles routing within the containerized environment.

```nginx
upstream backend_server {
  server web:8000;
}

server {
    listen 80;
    server_name _;

    # Django static files
    location /static/ {
        alias /var/www/django/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Django media files
    location /media/ {
        alias /var/www/django/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Send all other requests to Django
    location / {
      proxy_pass http://backend_server;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto https;  # Force HTTPS here
      proxy_set_header X-Forwarded-Host $http_host;
      proxy_set_header X-Forwarded-Server $http_host;
      proxy_redirect off;
    }
}
```

**Key responsibilities:**
- Efficiently serving static and media files directly
- Setting appropriate cache headers for static content
- Proxying API requests to the Django application
- Preserving client information in headers

### 3. Docker Compose Configuration

The Docker Compose setup orchestrates the containers:

```yaml
services:
  web:
    <<: &web # Image for production:
      image: "engine-sync-backend:prod"
      build:
        target: production_build
        context: .
        dockerfile: ./docker/django/Dockerfile
        args:
          DJANGO_ENV: production

      restart: unless-stopped
      volumes:
        - django-media:/var/www/django/media
        - django-locale:/code/locale

    command: bash ./docker/django/gunicorn.sh
    networks:
      - proxy-net

  nginx:
    build:
      context: .
      dockerfile: ./docker/nginx/Dockerfile
    restart: unless-stopped
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./docker/nginx/ci.sh:/etc/ci.sh
      - django-static:/var/www/django/static
      - django-media:/var/www/django/media
    depends_on:
      - web
    networks:
      - proxy-net
    ports:
      - "8081:80"

networks:
  proxy-net:

volumes:
  django-media:
  django-locale:
  django-static:
```

**Key aspects:**
- Two main services: the Django application (`web`) and Nginx
- Shared Docker network (`proxy-net`) for container communication
- Volume mounting for static and media files
- Exposing the Docker Nginx container on port 8081

## Request Flow and Routing

1. **Client makes a request** to https://your-domain.com
2. **Host Nginx** receives the request:
   - Terminates SSL (handles HTTPS)
   - Forwards the request to the Docker Nginx container on port 8081
3. **Docker Nginx** processes the request:
   - For `/static/*` or `/media/*` paths: serves files directly from mounted volumes
   - For all other paths: forwards the request to the Django application
4. **Django application** handles API requests and generates responses

## Static and Media File Handling

- **Static files** (CSS, JS, etc.):
  - Stored in a Docker volume (`django-static`)
  - Served directly by Docker Nginx from `/var/www/django/static/`
  - Cache headers set to 30 days for better performance

- **Media files** (user uploads, etc.):
  - Stored in a Docker volume (`django-media`)
  - Shared between Django (for writing) and Nginx (for serving)
  - Served directly by Docker Nginx from `/var/www/django/media/`
  - Cache headers set to 30 days

## Security Considerations

- SSL termination at the host level
- HTTP to HTTPS redirection
- Proper header forwarding to maintain client information
- Containerized environment isolation
