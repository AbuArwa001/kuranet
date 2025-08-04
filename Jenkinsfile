pipeline {
    agent none
    
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
                withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                    withEnv(["DJANGO_SECRET_KEY=${env.SECRET_KEY}"]) {
                        sh """
                            chmod +x ./scripts/integration_tests.sh || true
                            ./scripts/integration_tests.sh
                        """
                    }
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

                                            # Reinstall dependencies
                                            source ${VENV_PATH}/bin/activate || { echo "ERROR: Could not activate virtual environment. Exiting."; exit 1; }
                                            pip install -U pip || true # Allow pip upgrade to fail gracefully
                                            pip install -r requirements.txt || { echo "ERROR: Pip install failed. Exiting."; exit 1; }

                                            # Django operations
                                            python3 manage.py makemigrations users polls || { echo "ERROR: Makemigrations failed. Exiting."; exit 1; }
                                            python3 manage.py migrate --noinput || { echo "ERROR: Migrate failed. Exiting."; exit 1; }

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
                    // Archive test results and artifacts even if build fails
                    junit '**/test-results.xml' 
                    archiveArtifacts artifacts: '**/*-report.txt,**/test-results.xml', allowEmptyArchive: true
                    
                    // Clean up workspace to prevent disk space issues
                    cleanWs()
                }
            }
        }
        success {
            script {
                // Only send success notification if all previous stages succeeded
                if (currentBuild.result == 'SUCCESS') {
                    withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                        discordSend(
                            description: "Deployment Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                            link: env.BUILD_URL,
                            message: "Successfully deployed commit: ${sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}",
                            footer: "Deployed by Jenkins at ${new Date().format('yyyy-MM-dd HH:mm:ss')}",
                            color: '65280', // Green
                            title: "✅ Deployment Success",
                            titleLink: env.BUILD_URL,
                            thumbnail: "${env.BUILD_URL}/artifact/static/logo.png",
                            webhookURL: "${DISCORD_WEBHOOK_URL}"
                        )
                    }
                }
            }
        }
        failure {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    discordSend(
                        description: "Deployment Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        message: "Failed to deploy commit: ${sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}",
                        footer: "Failed at ${new Date().format('yyyy-MM-dd HH:mm:ss')}",
                        color: '16711680', // Red
                        title: "❌ Deployment Failure",
                        titleLink: env.BUILD_URL,
                        thumbnail: "${env.BUILD_URL}/artifact/static/logo.png",
                        webhookURL: "${DISCORD_WEBHOOK_URL}"
                    )
                }
            }
        }
        unstable {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    discordSend(
                        description: "Deployment Unstable: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        message: "Deployment completed with warnings for commit: ${sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}",
                        footer: "Completed at ${new Date().format('yyyy-MM-dd HH:mm:ss')}",
                        color: '16753920', // Orange
                        title: "⚠️ Deployment Unstable",
                        titleLink: env.BUILD_URL,
                        thumbnail: "${env.BUILD_URL}/artifact/static/logo.png",
                        webhookURL: "${DISCORD_WEBHOOK_URL}"
                    )
                }
            }
        }
    }
}