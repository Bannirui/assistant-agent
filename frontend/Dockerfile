FROM node:20-alpine

# 从docker-compose里面读环境变量
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
