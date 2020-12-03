FROM nginx
EXPOSE 80
RUN rm /etc/nginx/conf.d/default.conf
RUN rm -r /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf