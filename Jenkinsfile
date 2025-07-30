pipeline {
    agent none  # No global agent

    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        SERVERS = ['172.234.252.70', '172.234.253.249']
        DOCKER_IMAGE = "python:3.12-slim"  # Official Python image
    }

    stages {
        // Stage 1: Code Validation in Docker
        stage('Dockerized Tests') {
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '-v /tmp:/tmp --network=host'  # Mount temp volume
                    reuseNode true  # Runs on Jenkins host
                }
            }
            steps {
                sh '''
                    apt-get update && apt-get install -y git
                    git clone ${REPO} /tmp/repo
                    cd /tmp/repo
                    python -m venv /tmp/venv
                    . /tmp/venv/bin/activate
                    pip install -r requirements.txt
                    python manage.py test
                    flake8 .
                    bandit -r .
                '''
                post {
                    always {
                        sh 'rm -rf /tmp/repo /tmp/venv'  # Cleanup
                    }
                }
            }
        }

        // Stage 2: Bare Metal Deployment
        stage('Deploy to Production') {
            agent any  # Runs on Jenkins executor
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    SERVERS.each { server ->
                        sshagent(['deploy-key']) {
                            sh """
                                ssh ubuntu@${server} '
                                    cd /home/ubuntu/kuranet
                                    git pull origin main
                                    source .venv/bin/activate
                                    pip install -r requirements.txt
                                    python manage.py migrate
                                    sudo systemctl restart gunicorn
                                '
                            """
                        }
                    }
                }
            }
        }
    }
}