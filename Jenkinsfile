pipeline {
    agent any

    environment {
        // Make sure your credentials are set in Jenkins
        REDIS_PASSWORD = credentials('REDIS_PASSWORD')
        POSTGRES_PASSWORD = credentials('POSTGRES_PASSWORD')
        DB_USER = credentials('DB_USER')
        SECRET_KEY = credentials('SECRET_KEY')
        EMAIL_HOST_PASSWORD = credentials('EMAIL_HOST_PASSWORD')
        DEFAULT_FROM_EMAIL = credentials('DEFAULT_FROM_EMAIL')
        DEBUG = 'True'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/ShuhaibMuhammed175/task-service.git', branch: 'main'
            }
        }

        stage('Prepare .env') {
            steps {
                sh '''
                    echo "REDIS_PASSWORD=${REDIS_PASSWORD}" > .env
                    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
                    echo "DB_USER=${DB_USER}" >> .env
                    echo "SECRET_KEY=${SECRET_KEY}" >> .env
                    echo "DEBUG=${DEBUG}" >> .env
                    echo "EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}" >> .env
                    echo "DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL}" >> .env
                '''
            }
        }

        stage('Docker Compose Down') {
            steps {
                sh 'docker compose down --volumes'
            }
        }

        stage('Docker Compose Build & Up') {
            steps {
                sh 'docker compose up -d --build'
            }
        }

        stage('Make Migrations') {
            steps {
                sh 'docker exec auth_service python manage.py makemigrations'
            }
        }

        stage('Migrate') {
            steps {
                sh 'docker exec auth_service python manage.py migrate'
            }
        }

        stage('Create Superuser') {
            steps {
                sh 'docker exec auth_service python manage.py shell < create_superuser.py'
            }
        }

        stage('Run Test Cases') {
            steps {
                sh 'docker exec auth_service python manage.py test'
            }
        }
    }

    post {
        always {
            sh 'docker compose down --volumes'
        }
    }
}
