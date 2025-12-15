#!/bin/bash
# ViralLab Deployment Script
# Usage: ./deploy.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================================
# GCE/GCR Configuration
# ========================================
PROJECT_ID="gen-lang-client-0505571886"
IMAGE_NAME="virallab-app"
GCE_ZONE="us-central1-c"
GCE_INSTANCE="instance-20250725-190052"
GCE_IP="35.226.2.144"
APP_PORT="8888"
INTERNAL_PORT="8001"
# ========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ViralLab Deployment Script${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${RED}Error: .env file not found!${NC}"
        exit 1
    fi
    # Source .env file
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
}

# Load env vars for docker run command
get_env_flags() {
    echo "-e POSTGRES_USER=$POSTGRES_USER \
-e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
-e POSTGRES_DB=$POSTGRES_DB \
-e JWT_SECRET_KEY=$JWT_SECRET_KEY \
-e JWT_ALGORITHM=$JWT_ALGORITHM \
-e ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES \
-e REFRESH_TOKEN_EXPIRE_DAYS=$REFRESH_TOKEN_EXPIRE_DAYS \
-e OPENAI_API_KEY=$OPENAI_API_KEY \
-e YOUTUBE_API_KEY=$YOUTUBE_API_KEY \
-e GEMINI_API_KEY=$GEMINI_API_KEY \
-e R2_ACCOUNT_ID=$R2_ACCOUNT_ID \
-e R2_ACCESS_KEY_ID=$R2_ACCESS_KEY_ID \
-e R2_SECRET_ACCESS_KEY=$R2_SECRET_ACCESS_KEY \
-e R2_BUCKET_NAME=$R2_BUCKET_NAME \
-e R2_PUBLIC_URL=$R2_PUBLIC_URL \
-e STORAGE_MODE=$STORAGE_MODE \
-e IMAGE_PROVIDER=$IMAGE_PROVIDER \
-e ENHANCE_PROMPTS=$ENHANCE_PROMPTS \
-e ARK_API_KEY=$ARK_API_KEY \
-e ARK_MODEL_ID=$ARK_MODEL_ID \
-e PUBLIC_BASE_URL=http://$GCE_IP:$APP_PORT \
-e DATABASE_URL=postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@virallab-db:5432/$POSTGRES_DB"
}

print_header

case "$1" in
    # ================== LOCAL COMMANDS ==================
    start)
        check_env
        echo -e "${YELLOW}Starting ViralLab locally...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ ViralLab started!${NC}"
        echo -e "  Access at: http://localhost:$APP_PORT"
        ;;
    
    stop)
        echo -e "${YELLOW}Stopping ViralLab locally...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ ViralLab stopped!${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting ViralLab locally...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ ViralLab restarted!${NC}"
        ;;
    
    rebuild)
        check_env
        echo -e "${YELLOW}Rebuilding ViralLab locally...${NC}"
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}✓ ViralLab rebuilt and started!${NC}"
        echo -e "  Access at: http://localhost:$APP_PORT"
        ;;
    
    logs)
        echo -e "${YELLOW}Showing local logs (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
        ;;
    
    status)
        echo -e "${YELLOW}Local Container Status:${NC}"
        docker-compose ps
        echo ""
        echo -e "${YELLOW}Health Check:${NC}"
        curl -s http://localhost:$APP_PORT/health | python3 -m json.tool 2>/dev/null || echo "App not responding"
        ;;
    
    # ================== GCE DEPLOYMENT ==================
    deploy)
        check_env
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  Deploying to GCE: $GCE_INSTANCE ($GCE_IP)${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Step 1: Build Docker image for linux/amd64
        echo -e "${YELLOW}[1/4] Building Docker image for linux/amd64...${NC}"
        docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/$IMAGE_NAME:latest "$SCRIPT_DIR"
        
        # Step 2: Push to Google Container Registry
        echo -e "${YELLOW}[2/4] Pushing image to GCR...${NC}"
        docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
        
        # Step 3: Deploy to VM
        echo -e "${YELLOW}[3/4] Deploying to VM...${NC}"
        
        ENV_FLAGS=$(get_env_flags)
        
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            # Create Docker network if not exists
            sudo docker network create virallab-network 2>/dev/null || true
            
            # Create data directory for postgres
            sudo mkdir -p /opt/virallab/postgres_data
            
            # Start PostgreSQL if not running
            if ! sudo docker ps | grep -q virallab-db; then
                echo '🗄️ Starting PostgreSQL...'
                sudo docker rm virallab-db 2>/dev/null || true
                sudo docker run -d \\
                    --name virallab-db \\
                    --network virallab-network \\
                    --restart unless-stopped \\
                    -v /opt/virallab/postgres_data:/var/lib/postgresql/data \\
                    -e POSTGRES_USER=$POSTGRES_USER \\
                    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \\
                    -e POSTGRES_DB=$POSTGRES_DB \\
                    postgres:16-alpine
                echo '⏳ Waiting for PostgreSQL to start...'
                sleep 5
            fi
            
            # Pull latest app image
            echo '📥 Pulling latest image...'
            sudo docker pull gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
            
            # Stop and remove current app container
            sudo docker stop virallab-app 2>/dev/null || true
            sudo docker rm virallab-app 2>/dev/null || true
            
            # Start new app container
            echo '🚀 Starting ViralLab app...'
            sudo docker run -d \\
                --name virallab-app \\
                --network virallab-network \\
                --restart unless-stopped \\
                -p $APP_PORT:$INTERNAL_PORT \\
                $ENV_FLAGS \\
                gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
            
            echo ''
            echo '📊 Container status:'
            sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep virallab
        "
        
        # Step 4: Health check
        echo -e "${YELLOW}[4/4] Testing deployment...${NC}"
        sleep 5
        if curl -sf "http://$GCE_IP:$APP_PORT/health" > /dev/null; then
            echo -e "${GREEN}✓ Health check passed!${NC}"
        else
            echo -e "${YELLOW}⏳ App still starting, checking again in 10s...${NC}"
            sleep 10
            curl -s "http://$GCE_IP:$APP_PORT/health" | python3 -m json.tool 2>/dev/null || echo -e "${RED}Health check failed${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        echo -e "${GREEN}  🌍 App: http://$GCE_IP:$APP_PORT${NC}"
        echo -e "${GREEN}  📚 Docs: http://$GCE_IP:$APP_PORT/docs${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        ;;
    
    gce-start)
        echo -e "${YELLOW}Starting containers on GCE...${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            sudo docker start virallab-db virallab-app
        "
        echo -e "${GREEN}✓ Started!${NC}"
        ;;
    
    gce-stop)
        echo -e "${YELLOW}Stopping containers on GCE...${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            sudo docker stop virallab-app virallab-db
        "
        echo -e "${GREEN}✓ Stopped!${NC}"
        ;;
    
    gce-restart)
        echo -e "${YELLOW}Restarting app on GCE...${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            sudo docker restart virallab-app
        "
        echo -e "${GREEN}✓ Restarted!${NC}"
        ;;
    
    gce-logs)
        echo -e "${YELLOW}Showing GCE logs (Ctrl+C to exit)...${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            sudo docker logs -f virallab-app
        "
        ;;
    
    gce-status)
        echo -e "${YELLOW}GCE Container Status:${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE --command="
            sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'NAMES|virallab'
        "
        echo ""
        echo -e "${YELLOW}Health Check:${NC}"
        curl -s "http://$GCE_IP:$APP_PORT/health" | python3 -m json.tool 2>/dev/null || echo "App not responding"
        ;;
    
    gce-ssh)
        echo -e "${YELLOW}Connecting to GCE...${NC}"
        gcloud compute ssh $GCE_INSTANCE --zone=$GCE_ZONE
        ;;
    
    *)
        echo "Usage: $0 {command}"
        echo ""
        echo -e "${YELLOW}Local Commands:${NC}"
        echo "  start     - Start locally with docker-compose"
        echo "  stop      - Stop local containers"
        echo "  restart   - Restart local containers"
        echo "  rebuild   - Rebuild and start locally"
        echo "  logs      - View local logs"
        echo "  status    - Local status + health check"
        echo ""
        echo -e "${BLUE}GCE Deployment Commands:${NC}"
        echo "  deploy      - Build → Push to GCR → Deploy to VM"
        echo "  gce-start   - Start containers on GCE"
        echo "  gce-stop    - Stop containers on GCE"
        echo "  gce-restart - Restart app on GCE"
        echo "  gce-logs    - View GCE app logs"
        echo "  gce-status  - GCE status + health check"
        echo "  gce-ssh     - SSH into GCE instance"
        echo ""
        echo -e "${GREEN}GCE: $GCE_INSTANCE | IP: $GCE_IP:$APP_PORT${NC}"
        exit 1
        ;;
esac
