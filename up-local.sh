# Deployment script to run the full stack application using docker compose 

# Compose up the full stack application. Omit certbot. 
docker compose -f docker-compose.local.yml up frontend nginx backend db --build -d 

