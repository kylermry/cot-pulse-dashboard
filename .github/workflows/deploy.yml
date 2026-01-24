name: Deploy to DigitalOcean

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /var/www/cotpulse/cot_dashboard_v5
          git pull origin main
          source /var/www/cotpulse/venv/bin/activate
          pkill -f "reflex run"
          sleep 3
          nohup reflex run --env prod > /var/log/reflex.log 2>&1 &