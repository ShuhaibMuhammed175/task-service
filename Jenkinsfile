pipeline {
    agent any

    environment {
        # Environment variables for Docker Compose
        REDIS_PASSWORD = 'demo123'
        REDIS_HOST     = 'redis'
        REDIS_PORT     = '6379'
        POSTGRES_DB    = 'auth_service'
        POSTGRES_USER  = 'postgres'
        POSTGRES_PASSWORD = 'demo123'
    }

    stages {

        stage('Pull Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ShuhaibMuhammed175/task-service.git'
            }
        }

        stage('List Files') {
            steps {
                sh 'ls'
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    echo "Creating .env file in workspace..."
                    cat <<EOF > .env
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_HOST=${REDIS_HOST}
REDIS_PORT=${REDIS_PORT}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF
                    echo ".env file created."
                '''
            }
        }

        stage('Docker Compose Down & Up') {
            steps {
                sh '''
                    echo "Starting Docker Compose..."
                    docker compose down
                    docker compose up -d --build

                    echo "Waiting for Postgres and Redis to be ready..."
                    RETRIES=20
                    until docker exec postgres_db pg_isready -U ${POSTGRES_USER} || [ $RETRIES -eq 0 ]; do
                        echo "Waiting for Postgres..."
                        sleep 3
                        RETRIES=$((RETRIES-1))
                    done

                    RETRIES=20
                    until docker exec redis_server redis-cli -a ${REDIS_PASSWORD} ping | grep PONG || [ $RETRIES -eq 0 ]; do
                        echo "Waiting for Redis..."
                        sleep 3
                        RETRIES=$((RETRIES-1))
                    done

                    echo "All services are ready."
                '''
            }
        }

        stage('Make Migrations & Migrate') {
            steps {
                sh '''
                    echo "Running Django migrations..."
                    docker exec auth_service python manage.py makemigrations
                    docker exec auth_service python manage.py migrate
                '''
            }
        }

        stage('Create Superuser') {
            steps {
                sh '''
                    echo "Creating Django superuser..."
                    docker exec -i auth_service python manage.py shell < create_superuser.py
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "Running Django tests..."
                    docker exec auth_service python manage.py test
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Showing container status and logs for debugging:"
            sh '''
                docker ps -a
                echo "Logs for auth_service:"
                docker logs auth_service || echo "No logs available"
                echo "Logs for celery_worker:"
                docker logs celery_worker || echo "No logs available"
            '''
        }
    }
}
