FROM nginx:alpine

# Copy config file
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./docker/nginx/ci.sh /etc/ci.sh

RUN chmod +x /etc/ci.sh
