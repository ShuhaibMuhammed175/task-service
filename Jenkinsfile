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
        DEBUG                  = 'True'
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
                    printf "REDIS_PASSWORD='%s'\\n" "$REDIS_PASSWORD" > .env
                    printf "POSTGRES_PASSWORD='%s'\\n" "$POSTGRES_PASSWORD" >> .env
                    printf "DB_USER='%s'\\n" "$DB_USER" >> .env
                    printf "SECRET_KEY='%s'\\n" "$SECRET_KEY" >> .env
                    printf "DEBUG='%s'\\n" "$DEBUG" >> .env
                    printf "EMAIL_HOST_PASSWORD='%s'\\n" "$EMAIL_HOST_PASSWORD" >> .env
                    printf "DEFAULT_FROM_EMAIL='%s'\\n" "$DEFAULT_FROM_EMAIL" >> .env
                    printf "EMAIL_BACKEND='%s'\\n" "$EMAIL_BACKEND" >> .env
                    printf "EMAIL_HOST='%s'\\n" "$EMAIL_HOST" >> .env
                    printf "EMAIL_PORT='%s'\\n" "$EMAIL_PORT" >> .env
                    printf "EMAIL_USE_TLS='%s'\\n" "$EMAIL_USE_TLS" >> .env
                    printf "EMAIL_HOST_USER='%s'\\n" "$EMAIL_HOST_USER" >> .env
                    printf "CELERY_BROKER_URL='%s'\\n" "$CELERY_BROKER_URL" >> .env
                    printf "CELERY_RESULT_BACKEND='%s'\\n" "$CELERY_RESULT_BACKEND" >> .env
                    printf "LOCATION='%s'\\n" "$LOCATION" >> .env
                    printf "BASE_URL_FP='%s'\\n" "$BASE_URL_FP" >> .env
                '''
            }
        }

        stage('Docker Compose Down') {
            steps {
                sh 'docker compose down'
            }
        }

        stage('Docker Compose Build & Up') {
            steps {
                sh 'docker compose up -d --build'
            }
        }

        stage('Wait for Django') {
            steps {
                sh '''
                    echo "Waiting for auth_service to be ready..."
                    until docker exec auth_service python manage.py showmigrations; do
                        sleep 5
                    done
                '''
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
}
