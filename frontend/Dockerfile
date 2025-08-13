# frontend/Dockerfile
FROM node:20.19-alpine

WORKDIR /app

# Install deps
COPY package*.json ./
RUN npm ci

# Copy app
COPY . .

# Vite dev server runs on 8080
EXPOSE 8080

# Start Vite in dev mode, binding to all interfaces (important in Docker)
CMD ["npm","run","dev","--","--host","0.0.0.0","--port","8080"]

