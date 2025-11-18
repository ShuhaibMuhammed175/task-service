pipeline {
    agent any
    

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
