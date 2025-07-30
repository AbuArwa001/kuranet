pipeline {
    agent any
    environment {
        REPO = "https://github.com/AbuArwa001/kuranet.git"
        SERVERS = ['172.234.252.70', '172.234.253.249']
        SLACK_CHANNEL = '#deployments'
    }
    
    stages {
        // Stage 1: Code Validation
        stage('Code Quality Check') {
            steps {
                script {
                    try {
                        sh '''
                            python -m venv venv
                            source venv/bin/activate
                            pip install flake8 black isort
                            flake8 . --count --show-source --statistics
                            black --check .
                            isort --check-only .
                        '''
                    } catch (err) {
                        slackSend channel: SLACK_CHANNEL, 
                            message: "❌ Code quality issues detected in ${env.BUILD_URL}\n" +
                                     "Run these commands to fix:\n" +
                                     "```\n" +
                                     "black .\n" +
                                     "isort .\n" +
                                     "# Address flake8 warnings\n" +
                                     "```"
                        error("Code quality checks failed!")
                    }
                }
            }
        }

        // Stage 2: Security Scan
        stage('Security Scan') {
            steps {
                script {
                    def scanResult = sh(script: 'bandit -r . -f json -o bandit-report.json', returnStatus: true)
                    if (scanResult != 0) {
                        archiveArtifacts artifacts: 'bandit-report.json'
                        slackSend channel: SLACK_CHANNEL,
                            message: "⚠️ Security issues found. Review report: ${env.BUILD_URL}artifact/bandit-report.json"
                        // Continue but warn (modify to 'error' for strict blocking)
                    }
                }
            }
        }

        // Stage 3: Test Suite
        stage('Run Tests') {
            steps {
                script {
                    try {
                        sh '''
                            source venv/bin/activate
                            pip install -r requirements.txt
                            python manage.py test --noinput --verbosity=2
                        '''
                    } catch (err) {
                        slackSend channel: SLACK_CHANNEL,
                            message: "🔴 Tests failed in ${env.BUILD_URL}\n" +
                                     "To reproduce locally:\n" +
                                     "```\n" +
                                     "python manage.py test\n" +
                                     "```"
                        error("Test suite failed!")
                    }
                }
            }
        }

        // Stage 4: Safe Deployment
        stage('Rolling Deployment') {
            steps {
                script {
                    def failedServers = []
                    
                    SERVERS.each { server ->
                        try {
                            sshagent(['deploy-key']) {
                                // Create release folder with timestamp
                                sh """
                                    ssh ubuntu@${server} '
                                        cd /home/ubuntu
                                        release_dir="releases/\$(date +%Y%m%d_%H%M%S)"
                                        mkdir -p \$release_dir
                                        git clone ${REPO} \$release_dir
                                        cd \$release_dir
                                        
                                        # Build
                                        python -m venv .venv
                                        source .venv/bin/activate
                                        pip install -r requirements.txt
                                        python manage.py migrate
                                        python manage.py collectstatic --noinput
                                        
                                        # Health check before switch
                                        if ! curl -sf http://localhost:8000/health/; then
                                            echo "Health check failed for new version"
                                            exit 1
                                        fi
                                        
                                        # Atomic switch
                                        ln -sfn \$release_dir /home/ubuntu/kuranet
                                        sudo systemctl restart gunicorn
                                        
                                        # Verify after deployment
                                        sleep 5
                                        if ! curl -sf http://localhost:8000/health/; then
                                            echo "Post-deploy health check failed"
                                            exit 1
                                        fi
                                        
                                        # Cleanup old releases (keep last 3)
                                        ls -td /home/ubuntu/releases/* | tail -n +4 | xargs rm -rf
                                    '
                                """
                            }
                        } catch (err) {
                            failedServers << server
                            // Automatic rollback for this server
                            sh """
                                ssh ubuntu@${server} '
                                    cd /home/ubuntu
                                    if [ -L kuranet ]; then
                                        last_good=\$(readlink -f kuranet)
                                        ln -sfn \$last_good kuranet
                                        sudo systemctl restart gunicorn
                                    fi
                                '
                            """
                        }
                    }
                    
                    if (failedServers) {
                        slackSend channel: SLACK_CHANNEL,
                            message: "⚠️ Deployment partially failed. Servers ${failedServers} rolled back.\n" +
                                     "Successful servers: ${SERVERS - failedServers}\n" +
                                     "Investigate: ${env.BUILD_URL}"
                        error("Deployment failed on servers: ${failedServers}")
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean workspace
            deleteDir()
        }
        success {
            slackSend channel: SLACK_CHANNEL,
                message: "✅ Successfully deployed ${env.BUILD_URL}"
        }
        failure {
            // Additional failure analysis
            script {
                sh 'cat bandit-report.json || true'
                archiveArtifacts artifacts: '**/test*.xml,**/*.log'
            }
        }
    }
}