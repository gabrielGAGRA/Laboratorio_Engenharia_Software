FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
COPY packages/ ./packages/
COPY app/web/ ./app/web/
RUN npm install
RUN npm --prefix app/web run build

FROM nginx:alpine
COPY --from=build /app/app/web/dist/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
