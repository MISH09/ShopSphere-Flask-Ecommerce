pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID = '415457743365'
        ECR_REPOSITORY = 'shopsphere'
        IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t shopsphere:${BUILD_NUMBER} .'
                sh 'docker tag shopsphere:${BUILD_NUMBER} ${IMAGE_URI}:${BUILD_NUMBER}'
                sh 'docker tag shopsphere:${BUILD_NUMBER} ${IMAGE_URI}:latest'
            }
        }

        stage('Login to AWS ECR') {
            steps {
                sh '''
                    set -eu
                    aws ecr get-login-password --region "$AWS_REGION" |
                        docker login --username AWS --password-stdin \
                        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                '''
            }
        }

        stage('Push to AWS ECR') {
            steps {
                sh 'docker push ${IMAGE_URI}:${BUILD_NUMBER}'
                sh 'docker push ${IMAGE_URI}:latest'
            }
        }
    }

    post {
        success {
            echo 'ShopSphere image built and pushed to AWS ECR successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the console output for details.'
        }
    }
}

