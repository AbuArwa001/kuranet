pipeline {
    agent none
    
    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        WEB1_IP = "172.234.252.70"
        WEB2_IP = "172.234.253.249"
        DOCKER_IMAGE = "python:3.12-slim"
        APP_DIR = "~/kuranet"
        VENV_PATH = "${APP_DIR}/.venv"
    }

    stages {
        // CI PHASE START
        stage('Checkout') {
            agent any
            steps {
                checkout scm
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
                sh """
                    python -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install -r requirements.txt
                    python manage.py test kuranet.tests
                """
            }
        }

        stage('Static Analysis') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp --network=host'
                    reuseNode true
                }
            }
            steps {
                script {
                    // Install and run pylint
                    sh "pip install pylint"
                    sh "pylint kuranet/ --exit-zero"
                    
                    // Security scanning
                    sh "pip install bandit"
                    sh "bandit -r kuranet/"
                }
            }
        }
        // CI PHASE END

        // CD PHASE START
        stage('Deploy to Staging') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-u root -v /tmp:/tmp --network=host'
                    reuseNode true
                }
            }
            steps {
                script {
                    sshagent(['SSH_CREDENTIALS']) {
                        retry(3) {
                            sh """
                                ssh -vvv -o StrictHostKeyChecking=no ubuntu@${WEB1_IP} '
                                    cd ${APP_DIR} && \
                                    git pull && \
                                    python -m venv ${VENV_PATH} && \
                                    . ${VENV_PATH}/bin/activate && \
                                    pip install -r requirements.txt && \
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
                    // Run API tests against staging environment
                    sh "pip install pytest requests"
                    sh "python tests/integration_tests.py"
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
                    args '-u root -v /tmp:/tmp --network=host'
                    reuseNode true
                }
            }
            steps {
                script {
                    sshagent(['SSH_CREDENTIALS']) {
                        retry(3) {
                            sh """
                                ssh -vvv -o StrictHostKeyChecking=no ubuntu@${WEB2_IP} '
                                    cd ${APP_DIR} && \
                                    git pull && \
                                    python -m venv ${VENV_PATH} && \
                                    . ${VENV_PATH}/bin/activate && \
                                    pip install -r requirements.txt && \
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
            node('') { // Wrap node-dependent steps in a node block
                junit '**/test-reports/*.xml'
                archiveArtifacts artifacts: '**/lint-report.txt', allowEmptyArchive: true
            }
        }
        success {
            discordSend(
                description: "Deployment Successful",
                link: env.BUILD_URL,
                webhookURL: 'https://discord.com/api/webhooks/1400802617625415720/xlQybzuwDzCWwyGklwY2WXaahb02LiC3JodoCIv9KD06z0J59zPM_NKqATjutWdbm14Z'
            )
        }
        failure {
            discordSend(
                description: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                link: env.BUILD_URL,
                webhookURL: 'https://discord.com/api/webhooks/1400802617625415720/xlQybzuwDzCWwyGklwY2WXaahb02LiC3JodoCIv9KD06z0J59zPM_NKqATjutWdbm14Z'
            )
        }
    }
}
