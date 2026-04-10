FROM node:alpine AS builder

WORKDIR /app/frontend

# Instala dependencias do frontend com lockfile para build reproduzivel.
COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

# Copia o projeto Angular e gera bundle de producao.
COPY frontend/ ./

RUN npm run build -- --configuration production

FROM nginx:1.27-alpine AS runtime

# Configuracao do Nginx (SPA + reverse proxy das APIs do projeto).
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Angular 21 (@angular/build:application) gera saida em dist/frontend/browser.
COPY --from=builder /app/frontend/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]