FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# bind to all interfaces so your host can reach it
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]