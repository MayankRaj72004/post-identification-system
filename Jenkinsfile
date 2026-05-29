pipeline {

    agent any

    environment {
        APP_NAME        = "postal-system"
        DOCKER_IMAGE    = "postal-system"
        DOCKER_REGISTRY = "mayankraj8791"

        IMAGE_TAG       = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}"
        IMAGE_LATEST    = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest"

        CONTAINER_PORT  = "8501"
        HOST_PORT       = "8501"

        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('📥 Checkout') {
            steps {
                echo "═══ Checking out source code ═══"

                checkout scm

                script {

                    env.GIT_COMMIT_MSG = bat(
                        script: '@git log -1 --pretty=%%B',
                        returnStdout: true
                    ).trim()

                    env.GIT_AUTHOR = bat(
                        script: '@git log -1 --pretty=%%ae',
                        returnStdout: true
                    ).trim()

                    echo "Commit: ${env.GIT_COMMIT_MSG}"
                    echo "Author: ${env.GIT_AUTHOR}"
                }
            }
        }

        stage('⚙️ Setup Environment') {
            steps {

                echo "═══ Setting up Python environment ═══"

                bat '''
                    python --version

                    pip install --upgrade pip

                    pip install -r requirements.txt

                    pip install flake8 black isort pytest pytest-cov pandas

                    echo Environment Ready
                '''
            }
        }

        stage('🔍 Code Quality') {

            parallel {

                stage('Flake8 Lint') {
                    steps {

                        bat '''
                            flake8 *.py ^
                            --max-line-length=120 ^
                            --ignore=E501,W503,E203 ^
                            --statistics ^
                            --count
                        '''
                    }
                }

                stage('Black Format Check') {
                    steps {

                        bat '''
                            black --check --diff *.py
                        '''
                    }
                }

                stage('isort Import Check') {
                    steps {

                        bat '''
                            isort --check-only --diff *.py
                        '''
                    }
                }
            }
        }

        stage('🧪 Unit Tests') {

            steps {

                echo "═══ Running unit tests ═══"

                bat '''
                    if exist tests (
                        pytest tests/ -v ^
                        --cov=. ^
                        --cov-report=xml:coverage.xml ^
                        --cov-report=html:coverage-report ^
                        --junitxml=test-results.xml
                    ) else (
                        echo No tests directory found
                    )
                '''
            }

            post {

                always {

                    junit allowEmptyResults: true,
                          testResults: 'test-results.xml'

                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'coverage-report',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('📊 Verify Data') {

            steps {

                echo "═══ Verifying pincode.csv ═══"

                bat '''
python -c "import pandas as pd; df=pd.read_csv('pincode.csv'); print(df.head())"
                '''
            }
        }

        stage('🐳 Docker Build') {

            steps {

                echo "═══ Building Docker image ═══"

                bat '''
                    docker build ^
                    -t %IMAGE_TAG% ^
                    -t %IMAGE_LATEST% ^
                    .
                '''

                bat '''
                    docker images
                '''
            }
        }

        stage('💨 Smoke Test') {

            steps {

                echo "═══ Running Smoke Test ═══"

                bat '''
                    docker run -d ^
                    --name postal-smoke-test ^
                    -p 18501:8501 ^
                    %IMAGE_TAG%

                    timeout /t 20

                    curl http://localhost:18501

                    docker stop postal-smoke-test

                    docker rm postal-smoke-test
                '''
            }

            post {

                failure {

                    bat '''
                        docker stop postal-smoke-test
                        docker rm postal-smoke-test
                    '''
                }
            }
        }

        stage('📤 Push Image') {

            when {
                branch 'main'
            }

            steps {

                echo "═══ Pushing Docker Image ═══"

                bat '''
                    docker login -u %DOCKERHUB_CREDS_USR% -p %DOCKERHUB_CREDS_PSW%

                    docker push %IMAGE_TAG%

                    docker push %IMAGE_LATEST%
                '''
            }
        }

        stage('🚀 Deploy') {

            when {
                branch 'main'
            }

            steps {

                echo "═══ Deploying Container ═══"

                bat '''
                    docker stop %APP_NAME%

                    docker rm %APP_NAME%

                    docker run -d ^
                    --name %APP_NAME% ^
                    -p %HOST_PORT%:%CONTAINER_PORT% ^
                    %IMAGE_TAG%
                '''
            }
        }
    }

    post {

        success {

            echo """
BUILD SUCCESS
Job: ${JOB_NAME}
Build: #${BUILD_NUMBER}
Image: ${IMAGE_TAG}
"""
        }

        failure {

            echo """
BUILD FAILED
Job: ${JOB_NAME}
Build: #${BUILD_NUMBER}
"""
        }

        always {

            bat '''
                docker image prune -f
            '''

            cleanWs()
        }
    }
}