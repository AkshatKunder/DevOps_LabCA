pipeline {
    agent any

    environment {
        dockerImage = 'python:3.11-slim'
    }

    stages {
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'python -m pytest tests/'
            }
        }

        stage('Deploy') {
            steps {
                sh 'python run.py'
            }
        }
    }
}