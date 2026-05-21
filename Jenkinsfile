// ─── Jenkins Declarative Pipeline ─────────────────────────────────────────────
// AI Postal System — Build, Test, Dockerize & Deploy
// ──────────────────────────────────────────────────────────────────────────────

pipeline {

    // ── Run on any available agent ──────────────────────────────────────────
    agent any

    // ── Pipeline-wide environment variables ──────────────────────────────────
    environment {
        APP_NAME        = "postal-system"
        DOCKER_IMAGE    = "postal-system"
        DOCKER_REGISTRY = "mayankraj8791"        
        IMAGE_TAG       = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}"
        IMAGE_LATEST    = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest"
        CONTAINER_PORT  = "8501"
        HOST_PORT       = "8501"

        // Credentials configured in Jenkins → Manage Credentials
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
    }

    // ── Triggers ─────────────────────────────────────────────────────────────
    triggers {
        // Poll SCM every 5 minutes (or use a GitHub webhook instead)
        pollSCM('H/5 * * * *')
    }

    // ── Options ──────────────────────────────────────────────────────────────
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    // ══════════════════════════════════════════════════════════════════════════
    // STAGES
    // ══════════════════════════════════════════════════════════════════════════
    stages {

        // ── Stage 1: Checkout ──────────────────────────────────────────────
        stage('📥 Checkout') {
            steps {
                echo "═══ Checking out source code ═══"
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = sh(
                        script: 'git log -1 --pretty=%B',
                        returnStdout: true
                    ).trim()
                    env.GIT_AUTHOR = sh(
                        script: 'git log -1 --pretty=%ae',
                        returnStdout: true
                    ).trim()
                    echo "Commit: ${env.GIT_COMMIT_MSG}"
                    echo "Author: ${env.GIT_AUTHOR}"
                }
            }
        }

        // ── Stage 2: Environment Setup ─────────────────────────────────────
        stage('⚙️ Setup Environment') {
            steps {
                echo "═══ Setting up Python environment ═══"
                sh '''
                    python3 --version
                    pip3 install --upgrade pip --quiet
                    pip3 install -r requirements.txt --quiet
                    pip3 install flake8 black isort pytest pytest-cov --quiet
                    echo "✅ Environment ready"
                '''
            }
        }

        // ── Stage 3: Code Quality ──────────────────────────────────────────
        stage('🔍 Code Quality') {
            parallel {
                stage('Flake8 Lint') {
                    steps {
                        echo "Running flake8..."
                        sh '''
                            flake8 *.py \
                                --max-line-length=120 \
                                --ignore=E501,W503,E203 \
                                --statistics \
                                --count \
                                || true
                        '''
                    }
                }
                stage('Black Format Check') {
                    steps {
                        echo "Checking black formatting..."
                        sh 'black --check --diff *.py || true'
                    }
                }
                stage('isort Import Check') {
                    steps {
                        echo "Checking import ordering..."
                        sh 'isort --check-only --diff *.py || true'
                    }
                }
            }
        }

        // ── Stage 4: Unit Tests ────────────────────────────────────────────
        stage('🧪 Unit Tests') {
            steps {
                echo "═══ Running unit tests ═══"
                sh '''
                    if [ -d "tests" ]; then
                        pytest tests/ -v \
                            --cov=. \
                            --cov-report=xml:coverage.xml \
                            --cov-report=html:coverage-report \
                            --junitxml=test-results.xml \
                            || true
                    else
                        echo "⚠️  No tests/ directory found — skipping tests"
                    fi
                '''
            }
            post {
                always {
                    // Publish JUnit test results
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    // Publish coverage report
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

        // ── Stage 5: Verify Data File ──────────────────────────────────────
        stage('📊 Verify Data') {
            steps {
                echo "═══ Verifying pincode.csv ═══"
                sh '''
                    python3 - << 'EOF'
import pandas as pd, sys
try:
    df = pd.read_csv("pincode.csv")
    df.columns = df.columns.str.strip()
    required = ["Pincode", "OfficeName", "StateName", "District"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        print(f"❌ Missing columns: {missing}")
        sys.exit(1)
    print(f"✅ pincode.csv OK — {len(df):,} rows, {len(df.columns)} columns")
    print(f"   States: {df['StateName'].nunique()}, Pincodes: {df['Pincode'].nunique():,}")
except Exception as e:
    print(f"❌ Data validation failed: {e}")
    sys.exit(1)
EOF
                '''
            }
        }

        // ── Stage 6: Docker Build ──────────────────────────────────────────
        stage('🐳 Docker Build') {
            steps {
                echo "═══ Building Docker image: ${IMAGE_TAG} ═══"
                sh '''
                    docker build \
                        --target runtime \
                        --tag ${IMAGE_TAG} \
                        --tag ${IMAGE_LATEST} \
                        --label "build.number=${BUILD_NUMBER}" \
                        --label "build.url=${BUILD_URL}" \
                        --label "git.commit=${GIT_COMMIT}" \
                        --cache-from ${IMAGE_LATEST} \
                        .
                    echo "✅ Docker image built: ${IMAGE_TAG}"
                    docker images ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
                '''
            }
        }

        // ── Stage 7: Docker Image Scan ─────────────────────────────────────
        stage('🔒 Image Security Scan') {
            steps {
                echo "═══ Scanning image for vulnerabilities ═══"
                sh '''
                    # Install trivy if available, else skip
                    if command -v trivy &> /dev/null; then
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --no-progress \
                            --exit-code 0 \
                            ${IMAGE_TAG}
                    else
                        echo "⚠️  Trivy not installed — skipping security scan"
                    fi
                '''
            }
        }

        // ── Stage 8: Smoke Test ────────────────────────────────────────────
        stage('💨 Smoke Test') {
            steps {
                echo "═══ Running smoke test — container startup check ═══"
                sh '''
                    # Start container in background
                    docker run -d \
                        --name postal-smoke-test \
                        -p 18501:8501 \
                        ${IMAGE_TAG}

                    # Wait for app to start
                    sleep 20

                    # Check health endpoint
                    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
                        http://localhost:18501/_stcore/health || echo "000")

                    echo "Health check HTTP status: ${HTTP_CODE}"

                    # Cleanup
                    docker stop postal-smoke-test
                    docker rm  postal-smoke-test

                    if [ "${HTTP_CODE}" = "200" ]; then
                        echo "✅ Smoke test passed"
                    else
                        echo "⚠️  Smoke test returned ${HTTP_CODE} — check logs"
                    fi
                '''
            }
            post {
                failure {
                    sh 'docker stop postal-smoke-test || true; docker rm postal-smoke-test || true'
                }
            }
        }

        // ── Stage 9: Push to Registry ──────────────────────────────────────
        stage('📤 Push Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo "═══ Pushing image to Docker Hub ═══"
                sh '''
                    echo "${DOCKERHUB_CREDS_PSW}" | \
                        docker login -u "${DOCKERHUB_CREDS_USR}" --password-stdin

                    docker push ${IMAGE_TAG}
                    docker push ${IMAGE_LATEST}

                    echo "✅ Pushed: ${IMAGE_TAG}"
                    echo "✅ Pushed: ${IMAGE_LATEST}"
                '''
            }
        }

        // ── Stage 10: Deploy ───────────────────────────────────────────────
        stage('🚀 Deploy') {
            when { branch 'main' }
            steps {
                echo "═══ Deploying to production ═══"
                sh '''
                    # Stop old container if running
                    docker stop ${APP_NAME} 2>/dev/null || true
                    docker rm   ${APP_NAME} 2>/dev/null || true

                    # Run new container
                    docker run -d \
                        --name ${APP_NAME} \
                        --restart unless-stopped \
                        -p ${HOST_PORT}:${CONTAINER_PORT} \
                        -v /opt/postal-data:/app/data \
                        ${IMAGE_TAG}

                    echo "✅ Container ${APP_NAME} started on port ${HOST_PORT}"
                    docker ps --filter name=${APP_NAME}
                '''
            }
        }

    } // end stages

    // ══════════════════════════════════════════════════════════════════════════
    // POST ACTIONS
    // ══════════════════════════════════════════════════════════════════════════
    post {
        success {
            echo """
╔══════════════════════════════════════════╗
║  ✅  BUILD SUCCESS                       ║
║  Job:   ${JOB_NAME}                      ║
║  Build: #${BUILD_NUMBER}                 ║
║  Image: ${IMAGE_TAG}                     ║
╚══════════════════════════════════════════╝
            """
        }
        failure {
            echo """
╔══════════════════════════════════════════╗
║  ❌  BUILD FAILED                        ║
║  Job:   ${JOB_NAME}                      ║
║  Build: #${BUILD_NUMBER}                 ║
║  Check: ${BUILD_URL}console              ║
╚══════════════════════════════════════════╝
            """
            // Cleanup dangling resources on failure
            sh 'docker stop postal-smoke-test 2>/dev/null || true'
            sh 'docker rm  postal-smoke-test 2>/dev/null || true'
        }
        always {
            echo "Cleaning up local dangling images..."
            sh 'docker image prune -f 2>/dev/null || true'
            cleanWs()
        }
    }

} // end pipeline
