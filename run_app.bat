@echo off
cd %~dp0
docker compose -f docker-compose\local\compose.yaml --project-name nest-local up -d --build
