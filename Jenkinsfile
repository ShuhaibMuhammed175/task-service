pipeline {
    agent any

    stages {

        stage('Pull Code') {
            steps {
                git 'https://github.com/ShuhaibMuhammed175/task-service.git'
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
