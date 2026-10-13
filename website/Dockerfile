FROM nginx:1.31.2-alpine3.23

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html styles.css game.js /usr/share/nginx/html/
COPY images/ /usr/share/nginx/html/images/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
