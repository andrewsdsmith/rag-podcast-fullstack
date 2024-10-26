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

# Use the official Nginx image as the base image for serving the app
FROM nginx:1.21

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built Angular app from the previous stage to the Nginx html directory
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80