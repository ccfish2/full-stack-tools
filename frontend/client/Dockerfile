FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

# Clean install - fixes architecture mismatches between macOS and Linux
RUN npm ci --force || npm install --force

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]