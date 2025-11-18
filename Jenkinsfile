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

      
        stage('Test') {
            steps {
                sh 'echo $DEFAULT_FROM_EMAIL'
            }
        }

        stage('Pull Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ShuhaibMuhammed175/task-service.git'
            }
        }

        stage('run docker compose down') {
            steps {
                sh 'echo "Mdocker compose down..."'
                sh 'docker compose down'
            }
        }

        stage('docker build and up') {
            steps {
                sh 'echo "docker compose build..."'
                sh 'docker compose up -d --build'
            }
        }

        stage('Make Migrations') {
            steps {
                sh 'echo "make migrations..."'
                sh 'docker exec auth_service python manage.py makemigrations'
            }
        }
        stage('Migrate') {
            steps {
                sh 'echo "Migrate all ..."'
                sh 'docker exec auth_service python manage.py migrate'
            }
        }
        stage('create superuser') {
            steps {
                sh 'echo "created superuser..."'
                sh 'docker exec -i auth_service python manage.py shell < create_superuser.py'
            }
        }
        stage('Run Test Cases') {
            steps {
                sh 'echo "running test cases..."'
                sh 'docker exec auth_service python manage.py test'
            }
        }
    }
}
