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
                            sh """
                                for IP in ${WEB1_IP} ${WEB2_IP}; do
                                    ssh -o StrictHostKeyChecking=no ubuntu@\${IP} "
                                        cd ${APP_DIR} || exit 1
                                        
                                        # Reset all local changes and untracked files
                                        git reset --hard HEAD || exit 1
                                        git clean -fd || exit 1
                                        
                                        # Pull updates (use --ff-only to prevent merge commits)
                                        git pull --ff-only origin main || exit 1
                                        
                                        # Recreate .env if needed
                                        [ -f ~/.env ] && cp ~/.env . || true
                                        
                                        # Reinstall dependencies
                                        source ${VENV_PATH}/bin/activate
                                        pip install -r requirements.txt || exit 1
                                        
                                        # Django operations
                                        python manage.py makemigrations users polls || exit 1
                                        python manage.py migrate --noinput || exit 1
                                        python manage.py collectstatic --noinput || true
                                        
                                        sudo systemctl restart gunicorn || exit 1
                                        echo \"Deployed commit: \$(git rev-parse --short HEAD)\"
                                    " || {
                                        echo "Failed on \${IP}"; exit 1
                                    }
                                done
                            """
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
                // Wrap in node context since we're using agent none at top level
                node {
                    junit '**/test-results.xml'
                    archiveArtifacts artifacts: '**/*-report.txt,**/test-results.xml', allowEmptyArchive: true
                }
            }
        }
        success {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    discordSend(
                        description: "Deployment Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        imageURL: "${env.BUILD_URL}/artifact/static/logo.png",
                        footer: "Deployed by Jenkins",
                        webhookURL: "${DISCORD_WEBHOOK_URL}"
                    )
                }
            }
        }
        failure {
            script {
                withCredentials([string(credentialsId: 'discord-webhook-url', variable: 'DISCORD_WEBHOOK_URL')]) {
                    discordSend(
                        description: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        link: env.BUILD_URL,
                        imageURL: "${env.BUILD_URL}/artifact/static/logo.png",
                        footer: "Deployment failed",
                        webhookURL: "${DISCORD_WEBHOOK_URL}"
                    )
                }
            }
        }
    }
}