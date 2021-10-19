FROM node:12.13.0-alpine as build

COPY package.json ./
COPY yarn.lock ./
COPY . ./frontend
WORKDIR /frontend
RUN yarn install
RUN yarn build

FROM nginx:stable-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
