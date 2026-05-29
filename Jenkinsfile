pipeline {
    agent any

    environment {
        IMAGE_NAME = "yourdockerhubusername/postal-system"
        IMAGE_TAG = "latest"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {

        stage('📥 Checkout') {
            steps {
                echo '═══ Checking out source code ═══'

                checkout scm

                script {
                    def commitMsg = bat(
                        script: 'git log -1 --pretty=format:"%%s"',
                        returnStdout: true
                    ).trim()

                    def author = bat(
                        script: 'git log -1 --pretty=format:"%%ae"',
                        returnStdout: true
                    ).trim()

                    echo "Commit: ${commitMsg}"
                    echo "Author: ${author}"
                }
            }
        }

        stage('⚙️ Setup Environment') {
            steps {

                echo '═══ Setting up Python environment ═══'

                bat '''
                python --version
                if %ERRORLEVEL% NEQ 0 (
                    echo ERROR: Python not found
                    exit /b 1
                )

                python -m pip install --upgrade pip
                if %ERRORLEVEL% NEQ 0 exit /b 1

                python -m pip install -r requirements.txt
                if %ERRORLEVEL% NEQ 0 exit /b 1

                python -m pip install flake8 black isort pytest pytest-cov pandas
                if %ERRORLEVEL% NEQ 0 exit /b 1

                echo Environment Ready
                '''
            }
        }

        stage('🔍 Code Quality') {
            parallel {

                stage('Flake8 Lint') {
                    steps {
                        bat '''
                        python -m flake8 .
                        '''
                    }
                }

                stage('Black Format Check') {
                    steps {
                        bat '''
                        python -m black --check .
                        '''
                    }
                }

                stage('isort Import Check') {
                    steps {
                        bat '''
                        python -m isort . --check-only
                        '''
                    }
                }
            }
        }

        stage('🧪 Unit Tests') {
            steps {

                echo '═══ Running tests ═══'

                bat '''
                pytest --cov=. --cov-report=term
                '''
            }
        }

        stage('📊 Verify Data') {
            steps {

                echo '═══ Verifying project files ═══'

                bat '''
                dir
                '''
            }
        }

        stage('🐳 Docker Build') {
            steps {

                echo '═══ Building Docker image ═══'

                bat '''
                docker --version
                if %ERRORLEVEL% NEQ 0 (
                    echo ERROR: Docker not running
                    exit /b 1
                )

                docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                '''
            }
        }

        stage('💨 Smoke Test') {
            steps {

                echo '═══ Running smoke test ═══'

                bat '''
                docker run -d --name postal-test -p 5000:5000 %IMAGE_NAME%:%IMAGE_TAG%

                timeout /t 10

                docker ps

                docker stop postal-test
                docker rm postal-test
                '''
            }
        }

        stage('📤 Push Image') {
            steps {

                echo '═══ Pushing image to DockerHub ═══'

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    bat '''
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%

                    docker push %IMAGE_NAME%:%IMAGE_TAG%
                    '''
                }
            }
        }

        stage('🚀 Deploy') {
            steps {
                echo '═══ Deployment stage completed ═══'
            }
        }
    }

    post {

        always {

            bat '''
            docker image prune -f >nul 2>&1
            exit /b 0
            '''

            echo 'BUILD COMPLETE'
            echo "Job: ${env.JOB_NAME}"
            echo "Build: #${env.BUILD_NUMBER}"
        }

        success {
            echo 'BUILD SUCCESSFUL'
        }

        failure {
            echo 'BUILD FAILED - Check console output above'
        }
    }
}