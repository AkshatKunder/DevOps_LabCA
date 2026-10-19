pipeline {
    agent any

    environment {
        IMAGE_NAME = 'devops-theory-ia-quiz'
        CONTAINER_NAME = 'devops-theory-ia-quiz'
        SONAR_HOST_URL = 'http://host.docker.internal:9000'
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {

       stage('Build') {
    steps {
        bat '"C:\\Users\\aksha\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pip install -r requirements.txt'
    }
}

stage('Unit Tests') {
    steps {
        bat '"C:\\Users\\aksha\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest tests/test_app.py -v'
    }
}

stage('Integration Tests') {
    steps {
        bat '"C:\\Users\\aksha\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest tests/test_integration.py -v'
    }
}

stage('SonarQube Analysis') {
    steps {
        withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
            bat '''
                docker run --rm ^
                    -e SONAR_HOST_URL=%SONAR_HOST_URL% ^
                    -e SONAR_TOKEN=%SONAR_TOKEN% ^
                    -v "%WORKSPACE%:/usr/src" ^
                    sonarsource/sonar-scanner-cli:12.2.0.4256_8.1.0 ^
                    -Dsonar.working.directory=/usr/src/.scannerwork
            '''
        }
    }
}

stage('SonarQube Quality Gate') {
    steps {
        withEnv(['SONAR_HOST_URL=http://localhost:9000']) {
            withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                bat '"C:\\Users\\aksha\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" quality\\wait_for_quality_gate.py'
            }
        }
    }
}

        stage('Docker Build') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Trivy Security Scan') {
            steps {
                bat 'docker save %IMAGE_NAME%:%BUILD_NUMBER% -o quizgenius-image.tar'
                bat '''
                    docker run --rm ^
                        -v "%WORKSPACE%:/workspace" ^
                        aquasec/trivy:0.58.1 image ^
                        --input /workspace/quizgenius-image.tar ^
                        --scanners vuln ^
                        --severity HIGH,CRITICAL ^
                        --format json ^
                        --output /workspace/trivy-report.json ^
                        --exit-code 0
                '''
                bat '''
                    docker run --rm ^
                        -v "%WORKSPACE%:/workspace" ^
                        aquasec/trivy:0.58.1 image ^
                        --input /workspace/quizgenius-image.tar ^
                        --scanners vuln ^
                        --severity HIGH,CRITICAL ^
                        --exit-code 1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    docker inspect %CONTAINER_NAME% >nul 2>&1 && docker rm -f %CONTAINER_NAME%
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
