FROM node:24-alpine as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm ci --no-audit --no-fund|| npm install 

COPY . .

ARG API_URL
ENV VUE_APP_API_URL=${API_URL}
ENV NODE_ENV=production

RUN npm run build

FROM nginx:alpine as production-stage

COPY --from=build-stage /app/dist /var/www/frontend

RUN rm /etc/nginx/conf.d/default.conf

RUN chmod -R 755 /var/www/frontend

RUN chown -R nginx:nginx /var/www/frontend

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]