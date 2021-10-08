FROM node:12.13.0-alpine as build

WORKDIR /app/frontend
COPY package.json ./
COPY yarn.lock ./
RUN yarn install
COPY ./ ./
RUN npm run build

FROM nginx:stable-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
