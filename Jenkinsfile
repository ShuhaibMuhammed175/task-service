pipeline {
    agent any

    stages {

        stage('Pull Code') {
            steps {
                git 'https://github.com/ShuhaibMuhammed175/task-service.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python manage.py test'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t my-django-app .'
            }
        }
    }
}
