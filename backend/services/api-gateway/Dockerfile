# Use official Node.js 18 Alpine image
FROM node:18-alpine

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies for native modules (if needed)
RUN apk add --no-cache bash

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --production --ignore-scripts

# Copy all source code
COPY . .

# Expose the port the API Gateway listens on
EXPOSE 4000

# Start the app
CMD ["node", "index.js"]
