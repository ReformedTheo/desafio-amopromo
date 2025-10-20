FROM node:18-alpine as build

WORKDIR /app
# Copy package files first to leverage layer caching
COPY frontend/airport-frontend/package.json frontend/airport-frontend/package-lock.json* ./
# If package-lock.json exists, prefer `npm ci`, otherwise fall back to `npm install`
RUN npm install --silent
COPY frontend/airport-frontend/ ./
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
