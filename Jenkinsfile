pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID = '415457743365'
        ECR_REPOSITORY = 'shopsphere'
        IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"
        CONTAINER_NAME = 'shopsphere-container'
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
            aws ecr get-login-password --region "$AWS_REGION" > /tmp/ecr-password-${BUILD_NUMBER}
            docker login --username AWS --password-stdin \
                "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com" \
                < /tmp/ecr-password-${BUILD_NUMBER}
            rm -f /tmp/ecr-password-${BUILD_NUMBER}
        '''
    }
}

        stage('Push to AWS ECR') {
            steps {
                sh 'docker push ${IMAGE_URI}:${BUILD_NUMBER}'
                sh 'docker push ${IMAGE_URI}:latest'
            }
        }

        stage('Deploy to EC2') {
            steps {
                sh '''
                    set -eu

                    echo "Pulling the latest ShopSphere image..."
                    docker pull "${IMAGE_URI}:latest"

                    echo "Stopping the old container if it exists..."
                    docker rm -f "$CONTAINER_NAME" || true

                    echo "Starting the updated ShopSphere container..."
                    docker run -d \
                        --name "$CONTAINER_NAME" \
                        -p 5000:5000 \
                        --restart unless-stopped \
                        "${IMAGE_URI}:latest"

                    echo "Waiting for the application to start..."
                    sleep 5

                    if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" != "true" ]; then
                        docker logs "$CONTAINER_NAME" || true
                        echo "Deployment failed: container is not running."
                        exit 1
                    fi

                    echo "ShopSphere container is running."
                    docker ps --filter "name=$CONTAINER_NAME"
                '''
            }
        }
    }

    post {
        success {
            echo 'ShopSphere CI/CD pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the Console Output for details.'
        }
    }
}

