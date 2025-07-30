pipeline {
    agent any
    
    environment {
        WEB1_IP = 'web1-private-ip'
        WEB2_IP = 'web2-private-ip'
        SSH_CREDENTIALS = credentials('kranet-ssh-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    sshagent([SSH_CREDENTIALS]) {
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${WEB1_IP} 'cd /var/www/kuranet && pip install -r requirements.txt'"
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${WEB2_IP} 'cd /var/www/kuranet && pip install -r requirements.txt'"
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    sshagent([SSH_CREDENTIALS]) {
                        // Copy files to web servers
                        sh "rsync -avz -e 'ssh -o StrictHostKeyChecking=no' ./ ubuntu@${WEB1_IP}:/var/www/kranet/"
                        sh "rsync -avz -e 'ssh -o StrictHostKeyChecking=no' ./ ubuntu@${WEB2_IP}:/var/www/kranet/"
                        
                        // Restart Django on both servers
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${WEB1_IP} 'sudo systemctl restart kranet'"
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${WEB2_IP} 'sudo systemctl restart kranet'"
                    }
                }
            }
        }
        
        stage('Smoke Test') {
            steps {
                script {
                    // Verify deployment by hitting an API endpoint
                    sh "curl -I http://${WEB1_IP}:8000/api/polls/"
                    sh "curl -I http://${WEB2_IP}:8000/api/polls/"
                }
            }
        }
    }
    
    post {
        success {
            slackSend channel: '#devops', message: "Poll System Deployment Successful: ${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#devops', message: "Poll System Deployment Failed: ${env.BUILD_URL}"
        }
    }
}