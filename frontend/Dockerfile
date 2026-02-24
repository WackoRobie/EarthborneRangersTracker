FROM node:20-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm install

# Copy source (overridden by volume mount in dev, used as-is in prod builds)
COPY . .

CMD ["npm", "run", "dev"]
