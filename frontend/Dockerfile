# Use the official Node.js image as the base image
FROM node:20 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the entire project to the working directory
COPY . .

# Build the Angular app
RUN npm run build --configuration=production