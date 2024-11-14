# Deployment script to run the full stack application using docker compose 

# Stop and remove old containers, keeping volumes intact
echo "Stopping and removing old containers..."
docker compose down

# Prune unused images to free up space
echo "Removing unused Docker images to free up space..."
docker image prune -af

# Compose up the full stack application. Omit certbot. 
docker compose up frontend nginx backend db -d 

