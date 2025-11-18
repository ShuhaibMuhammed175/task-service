pipeline {
    agent any
    environment {
        SECRET_KEY='django-insecure-c3&)i2h%$ghbj%da1cic#gu2hqtyuvb1++fp(4y)7_*3to*j9r'
        DEBUG='False'
        DB_NAME='auth_service'
        DB_USER='postgres'
        DB_PASSWORD='demo123'
        DB_HOST='db'
        DB_PORT='5432'

        BASE_URL_FP='http://127.0.0.1:8000/accounts'

        
        EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST='smtp.gmail.com'
        EMAIL_PORT='587'
        EMAIL_USE_TLS='True'
        EMAIL_HOST_USER='mshuhaib176@gmail.com'  
        EMAIL_HOST_PASSWORD='zdrn wqrb ynzn obvi'
        DEFAULT_FROM_EMAIL='mshuhaib176@gmail.com'


        user='1000/day'     
        anon='20/day'       
        user_min='3/minute'
        user_day='10/day'
        resend_otp='2/minute'
        resend_otp_day='10/day'




        CELERY_BROKER_URL='redis://redis_server:6379/0'
        CELERY_RESULT_BACKEND='redis://redis_server:6379/0'

        LOCATION='redis://redis_server:6379/1'
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

        stage('Docker Compose Down & Up') {
            steps {
                sh '''
                    echo "Starting Docker..."
                    docker compose down
                    docker compose up -d --build
                '''
            }
        }

        stage('Make Migrations & Migrate') {
            steps {
                sh '''
                    echo "Make migrations"
                    docker exec auth_service python manage.py makemigrations
                    docker exec auth_service python manage.py migrate
                '''
            }
        }

        stage('Create Superuser') {
            steps {
                sh '''
                    echo "Creating superuser"
                    docker exec -i auth_service python manage.py shell < create_superuser.py
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "Running tests"
                    docker exec auth_service python manage.py test
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
        }
    }
}
