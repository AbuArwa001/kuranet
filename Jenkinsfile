pipeline {
    agent any
    
    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        WEB1_IP = "172.234.252.70"
        WEB2_IP = "172.234.253.249"
        DOCKER_IMAGE = "python:3.12-slim"
        APP_DIR = "~/kuranet"
        VENV_PATH = "${APP_DIR}/.venv"
        SSH_CREDENTIALS_ID = 'SSH_CREDENTIALS'
        DJANGO_SECRET_KEY = credentials('django-secret-key')
    }

    stages {
        // CI PHASE START
        stage('Checkout') {
            agent any
            steps {
                checkout scm
            }
        }

        stage('Security Scan') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                script {
                    sh "pip install bandit safety"
                    
                    // Bandit scan with threshold
                    def banditExit = sh(
                        script: "bandit -r kuranet/ -ll",
                        returnStatus: true
                    )
                    
                    // Dependency vulnerability check
                    sh "safety check --full-report"
                    
                    if (banditExit != 0) {
                        error("Security scan failed: Bandit found critical issues")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '**/bandit-report.*,**/safety-report.*', allowEmptyArchive: true
                }
            }
        }

        stage('Static Analysis') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                sh """
                    pip install pylint
                    pylint kuranet/ --exit-zero > pylint-report.txt
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pylint-report.txt', allowEmptyArchive: true
                }
            }
        }
        // CI PHASE END

        stage('Integration Tests') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'django-secret-key', variable: 'DJANGO_SECRET_KEY')
                ]) {
                    sh """
                        chmod +x ./scripts/integration_tests.sh || true
                        ./scripts/integration_tests.sh
                    """
                }
            }
        }


        stage('Deploy to Production') {
            agent any
            steps {
                sshagent(credentials: [SSH_CREDENTIALS_ID]) {
                    withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                        retry(3) {
                            script {
                                // Correct iteration: IPs should be space-separated
                                def web_ips = "${WEB1_IP} ${WEB2_IP}".split(' ')
                                for (ip in web_ips) {
                                    echo "Deploying to ${ip}..."
                                    sh """
                                        ssh -o StrictHostKeyChecking=no ubuntu@${ip} "
                                            # First configure passwordless sudo for deployment
                                            # (This comment refers to a manual step or a separate configuration task.
                                            # This script does not configure passwordless sudo itself.)

                                            # Navigate to the application directory
                                            cd ${APP_DIR} || { echo "ERROR: Could not change to directory ${APP_DIR}. Exiting."; exit 1; }

                                            # Reset repository state
                                            git reset --hard HEAD || { echo "ERROR: Git reset failed. Exiting."; exit 1; }

                                            # Clean static files using passwordless sudo
                                            sudo /bin/rm -rf ${APP_DIR}/static/ || true
                                            sudo /bin/rm -rf ${APP_DIR}/staticfiles/ || true
                                            mkdir -p staticfiles || true
                                            mkdir -p static || true

                                            # Pull updates safely
                                            git fetch origin main || { echo "ERROR: Git fetch failed. Exiting."; exit 1; }
                                            git checkout main || { echo "ERROR: Git checkout failed. Exiting."; exit 1; }
                                            git reset --hard origin/main || { echo "ERROR: Git reset hard failed. Exiting."; exit 1; }

                                            # Set correct permissions for the project directory and virtual environment
                                            # This is crucial to prevent 'Permission denied' errors during pip install
                                            sudo chown -R ubuntu:ubuntu ${APP_DIR}/ || { echo "ERROR: Failed to set ownership for APP_DIR. Exiting."; exit 1; }
                                            sudo chown -R ubuntu:ubuntu ${VENV_PATH}/ || { echo "ERROR: Failed to set ownership for VENV_PATH. Exiting."; exit 1; }

                                            # Reinstall dependencies
                                            source ${VENV_PATH}/bin/activate || { echo "ERROR: Could not activate virtual environment. Exiting."; exit 1; }
                                            pip install -U pip || true # Allow pip upgrade to fail gracefully
                                            pip install -r requirements.txt || { echo "ERROR: Pip install failed. Exiting."; exit 1; }

                                            # Django operations
                                            python3 manage.py makemigrations users polls || { echo "ERROR: Makemigrations failed. Exiting."; exit 1; }
                                            python3 manage.py migrate --noinput || { echo "ERROR: Migrate failed. Exiting."; exit 1; }

                                            # seed data
                                            # python3 manage.py seed || { echo "ERROR: Seed data failed. Exiting."; exit 1; }

                                            # Collect static with correct permissions
                                            python3 manage.py collectstatic --noinput || true
                                            sudo chown -R www-data:www-data static/ || true
                                            sudo chown -R www-data:www-data staticfiles/ || true

                                            # Restart services using passwordless sudo
                                            sudo systemctl restart gunicorn || { echo "ERROR: Gunicorn restart failed. Exiting."; exit 1; }
                                            echo "Deployed commit: \$(git rev-parse --short HEAD)"
                                        " || {
                                            echo "Deployment failed on ${ip}"; exit 1
                                        }
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }
        // CD PHASE END
    }

    post {
        always {
            script {
                node {
                    // Archive reports (no cleanup)
                    junit testResults: '**/test-results.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'bandit-report.xml, safety-report.json, pylint-report.txt', allowEmptyArchive: true
                    
                    // Skip cleanWs entirely (remove or disable it)
                    // cleanWs(deleteDirs: false)  // Optional: Minimal cleanup if needed
                }
            }
        }
        success {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    def commit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def coverage = sh(script: 'grep -oP "(?<=<pc_cov>)[0-9.]+" coverage.xml || echo "N/A"', returnStdout: true).trim()

                    discordSend(
                        webhookURL: env.DISCORD_WEBHOOK_URL,
                        description: "✅ Deployment Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        title: "Deployed commit: ${commit}",
                        footer: "Test coverage: ${coverage}%",
                    )
                }
            }
        }

        failure {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    discordSend(
                        webhookURL: env.DISCORD_WEBHOOK_URL,
                        description: "❌ Deployment Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        title: "Failed commit: ${sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}",
                        footer: "Check the build logs for details.",
                    )
                }
            }
        }

        unstable {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    def issues = sh(script: '''
                        echo "Bandit: $(test -f bandit-report.xml && grep -c "<issue" bandit-report.xml || echo 0)"
                        echo "Safety: $(test -f safety-report.json && jq length safety-report.json || echo 0)"
                        echo "Pylint: $(test -f pylint-report.txt && grep -c ": [CRWEF]" pylint-report.txt || echo 0)"
                    ''', returnStdout: true).trim()

                    discordSend(
                        webhookURL: env.DISCORD_WEBHOOK_URL,
                        description: "⚠️ Deployment Unstable: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        title: "Unstable issues detected",
                        footer: "${issues}",
                    )
                }
            }
        }
    }

}
