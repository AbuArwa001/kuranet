pipeline {
    agent none
    
    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        WEB1_IP = "172.234.252.70"
        WEB2_IP = "172.234.253.249"
        DOCKER_IMAGE = "python:3.12-slim"
        APP_DIR = "~/kuranet"
        VENV_PATH = "${APP_DIR}/.venv"
        SSH_CREDENTIALS_ID = 'ssh-credentials'
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

        stage('Unit Tests') {
            steps {
                sh '''
                    # Create fresh virtualenv
                    python -m venv .venv
                    source .venv/bin/activate
                    
                    # Install with coverage support
                    pip install -r requirements.txt pytest-xdist
                    
                    # Run tests with coverage
                    pytest -c pytest.ini
                    
                    # Fail if coverage too low
                    if [ $(grep -oP 'coverage.*\\K\\d+' coverage.xml) -lt 80 ]; then
                        echo "Coverage below 80%"
                        exit 1
                    fi
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')]
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
                            python -m venv ${VENV_PATH}
                            . ${VENV_PATH}/bin/activate
                            pip install -r requirements.txt
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
            agent any
            steps {
                sshagent(credentials: [SSH_CREDENTIALS_ID]) {
                    withCredentials([string(credentialsId: 'django-secret-key', variable: 'SECRET_KEY')]) {
                        retry(3) {
                            sh """
                                for IP in ${WEB1_IP} ${WEB2_IP}; do
                                    TIMESTAMP=\$(date +%Y%m%d_%H%M) && \\
                                    ssh -o StrictHostKeyChecking=no ubuntu@\${IP} '
                                        mv ${APP_DIR} ${APP_DIR}_bak_\${TIMESTAMP} && \\
                                        mkdir -p ${APP_DIR} && \\
                                        git clone ${REPO} ~/ && \\
                                        cp ~/.env ${APP_DIR} && \\
                                        cd ${APP_DIR} && \\
                                        python -m venv ${VENV_PATH} && \\
                                        . ${VENV_PATH}/bin/activate && \\
                                        pip install -r requirements.txt && \\
                                        python manage.py makemigrations users polls && \\
                                        python manage.py migrate && \\
                                        python manage.py collectstatic --noinput && \\
                                        sudo systemctl restart gunicorn
                                    '
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
                        webhookURL: "${DISCORD_WEBHOOK_URL}"
                    )
                }
            }
        }
    }
}