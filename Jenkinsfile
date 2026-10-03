pipeline {
    agent any

    environment {
        IMAGE_NAME = 'devops-theory-ia-quiz'
        CONTAINER_NAME = 'devops-theory-ia-quiz'
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {

        stage('Build') {
            steps {
                bat '"D:\\Aaryan\\anaconda\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat '"D:\\Aaryan\\anaconda\\python.exe" -m pytest tests/'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    docker rm -f %CONTAINER_NAME% || exit /b 0
                    docker run -d ^
                        --name %CONTAINER_NAME% ^
                        -p 5000:5000 ^
                        -e GEMINI_API_KEY=%GEMINI_API_KEY% ^
                        %IMAGE_NAME%:latest
                '''
            }
        }
    }
}


// CI/CD pipeline