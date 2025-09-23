pipeline {
  agent any

  environment {
    IMAGE_NAME = 'sentiment-api'
    REGISTRY    = credentials('docker-registry-url')    // e.g. docker.io/youruser
    REGISTRY_CREDS = credentials('docker-registry-creds')
    DEPLOY_HOST = credentials('deploy-ssh-host')         // e.g. user@server
    DOCKER_COMPOSE_PATH = '/opt/sentiment'               // remote path
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python & Test') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt -r requirements-dev.txt
          pytest -q --junitxml=reports/test-results.xml
        '''
      }
      post {
        always {
          junit 'reports/test-results.xml'
        }
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          docker build -t $IMAGE_NAME:$GIT_COMMIT .
          docker tag $IMAGE_NAME:$GIT_COMMIT $REGISTRY/$IMAGE_NAME:$GIT_COMMIT
        '''
      }
    }

    stage('Push (main only)') {
      when { branch 'main' }
      steps {
        sh '''
          echo $REGISTRY_CREDS_PSW | docker login $REGISTRY -u $REGISTRY_CREDS_USR --password-stdin
          docker push $REGISTRY/$IMAGE_NAME:$GIT_COMMIT
          docker tag $REGISTRY/$IMAGE_NAME:$GIT_COMMIT $REGISTRY/$IMAGE_NAME:latest
          docker push $REGISTRY/$IMAGE_NAME:latest
        '''
      }
    }

    stage('Deploy') {
      steps {
        sh '''
          ssh -o StrictHostKeyChecking=no $DEPLOY_HOST '
            set -e
            mkdir -p $DOCKER_COMPOSE_PATH
            cd $DOCKER_COMPOSE_PATH
            # pull newest image (if using registry) or build on host
            docker pull $REGISTRY/$IMAGE_NAME:latest || true
            # write compose file if not present (first time) or update image tag
            # (here we assume the compose in repo is used during first provision)
            docker compose down || true
            docker compose up -d --build
          '
        '''
      }
    }
  }

  post {
    success { echo "Pipeline completed successfully." }
    failure { echo "Pipeline failed." }
  }
}
