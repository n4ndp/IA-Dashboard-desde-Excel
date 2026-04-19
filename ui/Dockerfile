FROM node:20-alpine AS build
WORKDIR /app
ARG BACKEND_URL=http://backend:8000
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV BACKEND_URL=${BACKEND_URL}
ENTRYPOINT ["/entrypoint.sh"]
