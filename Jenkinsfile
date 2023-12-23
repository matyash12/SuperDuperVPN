pipeline {
    agent any

    environment {
        LOCAL_DOCKER_SERVER = 'unix:///var/run/docker.sock' // Replace with your local Docker server address
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Copy .env file to workspace') {
            steps {
                withCredentials([file(credentialsId: 'SUPER_DUPER_VPN_ENV_FILE', variable: 'env_file')]) {
                    script {
                        def envContent = readFile(env_file)
                        writeFile file: '.env', text: envContent
                    }
                }
            }
        }

        stage('Copy settings.py to django app') {
            steps {
                withCredentials([file(credentialsId: 'SUPER_DUPER_VPN_settings_py', variable: 'settings_py')]) {
                    script {
                        def appContent = readFile(settings_py)
                        writeFile file: 'mysite/mysite/settings.py', text: appContent
                    }
                }
            }
        }
        stage('Copy conf.conf to nginx') {
            steps {
                withCredentials([file(credentialsId: 'SUPER_DUPER_VPN_conf_conf', variable: 'conf_conf')]) {
                    script {
                        def appContent = readFile(conf_conf)
                        writeFile file: 'docker/nginx/conf.conf', text: appContent
                    }
                }
            }
        }
        

        stage('Run "docker compose up --build -d"') {
            steps {
                script {
                    sh 'docker compose up --build -d'
                }
            }
        }
    }

    post {
        success {
            echo 'Build and local deployment successful!'
        }

        failure {
            echo 'Build or local deployment failed!'
        }
    }
}
