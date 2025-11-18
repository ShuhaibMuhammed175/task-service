pipeline {
    agent any

    environment {
        REDIS_PASSWORD         = credentials('redis-pass')
        POSTGRES_PASSWORD      = credentials('postgres-pass')
        DB_USER                = credentials('DB_USER')
        SECRET_KEY             = credentials('django-key')

        EMAIL_BACKEND          = credentials('EMAIL_BACKEND')
        EMAIL_HOST             = credentials('EMAIL_HOST')
        EMAIL_PORT             = credentials('EMAIL_PORT')
        EMAIL_USE_TLS          = credentials('EMAIL_USE_TLS')
        EMAIL_HOST_USER        = credentials('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD    = credentials('EMAIL_HOST_PASSWORD')
        DEFAULT_FROM_EMAIL     = credentials('DEFAULT_FROM_EMAIL')

        CELERY_BROKER_URL      = credentials('CELERY_BROKER_URL')
        CELERY_RESULT_BACKEND  = credentials('CELERY_RESULT_BACKEND')

        LOCATION               = credentials('LOCATION')
        BASE_URL_FP            = credentials('BASE_URL_FP')
    }

    stages {

        stage('Pull Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ShuhaibMuhammed175/task-service.git'
            }
        }

        stage('Prepare .env') {
            steps {
                sh '''
                echo "REDIS_PASSWORD=$REDIS_PASSWORD" > .env
                echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env
                echo "DB_USER=$DB_USER" >> .env
                echo "SECRET_KEY=$SECRET_KEY" >> .env

                echo "EMAIL_BACKEND=$EMAIL_BACKEND" >> .env
                echo "EMAIL_HOST=$EMAIL_HOST" >> .env
                echo "EMAIL_PORT=$EMAIL_PORT" >> .env
                echo "EMAIL_USE_TLS=$EMAIL_USE_TLS" >> .env
                echo "EMAIL_HOST_USER=$EMAIL_HOST_USER" >> .env
                echo "EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD" >> .env
                echo "DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL" >> .env

                echo "CELERY_BROKER_URL=$CELERY_BROKER_URL" >> .env
                echo "CELERY_RESULT_BACKEND=$CELERY_RESULT_BACKEND" >> .env

                echo "LOCATION=$LOCATION" >> .env
                echo "BASE_URL_FP=$BASE_URL_FP" >> .env
                '''
            }
        }

        stage('Docker Compose Down') {
            steps {
                sh 'docker compose down'
            }
        }

        stage('Docker Build & Up') {
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
                sh 'docker exec -i auth_service python manage.py shell < create_superuser.py'
            }
        }

        stage('Run Test Cases') {
            steps {
                sh 'docker exec auth_service python manage.py test'
            }
        }
    }
}
