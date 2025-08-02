pipeline {
    agent none
    
    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        WEB1_IP = "172.234.252.70"
        WEB2_IP = "172.234.253.249"
        DOCKER_IMAGE = "python:3.12-slim"
        APP_DIR = "~/kuranet"
        VENV_PATH = "${APP_DIR}/.venv"
        SSH_CREDENTIALS = credentials('ssh-credentials')
        DISCORD_WEBHOOK_URL = credentials('discord-webhook-url')
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
        }

        stage('Unit Tests') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                    sh """
                        python -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        pip install -r requirements.txt
                        export DJANGO_SECRET_KEY=${SECRET_KEY}
                        python manage.py test polls.tests --verbosity=2 --failfast
                    """
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
                archiveArtifacts artifacts: 'pylint-report.txt'
            }
        }
        // CI PHASE END

        // CD PHASE START
        stage('Deploy to Staging') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                sshagent(['SSH_CREDENTIALS']) {
                    withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                        retry(3) {
                            sh """
                                ssh -o StrictHostKeyChecking=no ubuntu@${WEB1_IP} '
                                    cd ${APP_DIR} && \
                                    git pull && \
                                    python -m venv ${VENV_PATH} && \
                                    . ${VENV_PATH}/bin/activate && \
                                    pip install -r requirements.txt && \
                                    export DJANGO_SECRET_KEY=${SECRET_KEY} && \
                                    python manage.py migrate && \
                                    sudo systemctl restart gunicorn
                                '
                            """
                        }
                    }
                }
            }
        }

        stage('Integration Tests') {
            agent any
            steps {
                script {
                    withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                        sh """
                            pip install pytest requests
                            export DJANGO_SECRET_KEY=${SECRET_KEY}
                            python tests/integration_tests.py
                        """
                    }
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp'
                    reuseNode true
                }
            }
            steps {
                sshagent(['SSH_CREDENTIALS']) {
                    withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                        retry(3) {
                            sh """
                                ssh -o StrictHostKeyChecking=no ubuntu@${WEB2_IP} '
                                    cd ${APP_DIR} && \
                                    git pull && \
                                    python -m venv ${VENV_PATH} && \
                                    . ${VENV_PATH}/bin/activate && \
                                    pip install -r requirements.txt && \
                                    export DJANGO_SECRET_KEY=${SECRET_KEY} && \
                                    python manage.py migrate && \
                                    sudo systemctl restart gunicorn
                                '
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
            junit '**/test-reports/*.xml'
            archiveArtifacts artifacts: '**/*-report.txt', allowEmptyArchive: true
        }
        success {
            script {
                discordSend(
                    description: "Deployment Successful",
                    link: env.BUILD_URL,
                    webhookURL: "${DISCORD_WEBHOOK_URL}"
                )
            }
        }
        failure {
            script {
                discordSend(
                    description: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                    link: env.BUILD_URL,
                    webhookURL: "${DISCORD_WEBHOOK_URL}"
                )
            }
        }
    }
}