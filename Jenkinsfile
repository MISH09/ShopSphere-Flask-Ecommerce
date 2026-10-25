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
                    PASSWORD_FILE="/tmp/ecr-password-${BUILD_NUMBER}"
                    trap 'rm -f "$PASSWORD_FILE"' EXIT

                    aws ecr get-login-password --region "$AWS_REGION" > "$PASSWORD_FILE"

                    docker login \
                        --username AWS \
                        --password-stdin \
                        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com" \
                        < "$PASSWORD_FILE"
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

                    echo "Pulling ShopSphere image..."
                    docker pull "${IMAGE_URI}:${BUILD_NUMBER}"

                    echo "Stopping the previous container if present..."
                    docker rm -f "$CONTAINER_NAME" || true

                    echo "Starting the updated ShopSphere container..."
                    docker run -d \
                        --name "$CONTAINER_NAME" \
                        -p 5000:5000 \
                        --restart unless-stopped \
                        "${IMAGE_URI}:${BUILD_NUMBER}"

                    sleep 5

                    if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" != "true" ]; then
                        docker logs "$CONTAINER_NAME" || true
                        echo "EC2 deployment failed."
                        exit 1
                    fi

                    echo "EC2 deployment successful."
                    docker ps --filter "name=$CONTAINER_NAME"
                '''
            }
        }

        stage('Login to ECR on Windows Agent') {
            agent {
                label 'shopsphere-windows'
            }
            steps {
                bat '''
                    @echo off
                    setlocal

                    set "PASSWORD_FILE=%TEMP%\\ecr-password-%BUILD_NUMBER%.txt"

                    aws ecr get-login-password --region "%AWS_REGION%" > "%PASSWORD_FILE%"
                    if errorlevel 1 (
                        del "%PASSWORD_FILE%" 2>nul
                        exit /b 1
                    )

                    docker login --username AWS --password-stdin 415457743365.dkr.ecr.ap-south-1.amazonaws.com < "%PASSWORD_FILE%"
                    set "LOGIN_RESULT=%ERRORLEVEL%"

                    del "%PASSWORD_FILE%" 2>nul

                    if not "%LOGIN_RESULT%"=="0" exit /b 1
                    endlocal
                '''
            }
        }

        stage('Deploy to Minikube') {
            agent {
                label 'shopsphere-windows'
            }
            steps {
                bat '''
                    @echo off
                    setlocal

                    echo Checking Minikube...
                    kubectl config current-context
                    if errorlevel 1 exit /b 1

                    echo Pulling this Jenkins build from ECR...
                    docker pull "%IMAGE_URI%:%BUILD_NUMBER%"
                    if errorlevel 1 exit /b 1

                    echo Loading the image into Minikube...
                    minikube image load "%IMAGE_URI%:%BUILD_NUMBER%"
                    if errorlevel 1 exit /b 1

                    echo Updating the Kubernetes deployment...
                    kubectl set image deployment/shopsphere shopsphere="%IMAGE_URI%:%BUILD_NUMBER%"
                    if errorlevel 1 exit /b 1

                    echo Waiting for the rollout...
                    kubectl rollout status deployment/shopsphere --timeout=180s
                    if errorlevel 1 exit /b 1

                    echo Verifying the running pods...
                    kubectl get pods -l app=shopsphere -o wide

                    echo Verifying the deployment...
                    kubectl get deployment shopsphere

                    endlocal
                '''
            }
        }
    }

    post {
        success {
            echo 'ShopSphere CI/CD completed successfully, including Minikube deployment!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output to identify the failed stage.'
        }
    }
}