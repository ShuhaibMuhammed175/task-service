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
                sh 'ls -la'
            }
        }

        stage('Docker Build and Up') {
            steps {
                sh '''
                    echo "Stopping old containers..."
                    docker compose down

                    echo "Building and starting new containers..."
                    docker compose up -d --build
                '''
            }
        }

        stage('Wait for Database') {
            steps {
                sh '''
                    echo "Waiting for PostgreSQL to be ready..."
                    docker exec auth_service python wait_for_db.py
                '''
            }
        }

        stage('Migrate Database') {
            steps {
                sh '''
                    echo "Applying migrations..."
                    docker exec auth_service python manage.py makemigrations --noinput
                    docker exec auth_service python manage.py migrate --noinput
                '''
            }
        }

        stage('Create Superuser') {
            steps {
                sh '''
                    echo "Creating superuser..."
                    docker exec -i auth_service python manage.py shell < create_superuser.py
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "Running tests..."
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
