pipeline {
  agent any

  environment {
    IMAGE_NAME     = 'sentiment-api'
    REGISTRY_HOST  = credentials('docker-registry-url')      // es: docker.io/matteoferrillo
    DOCKERHUB      = credentials('docker-registry-creds')    // user/token con RW
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Test (Python in container)') {
      steps {
        sh '''
          set -e
          docker run --rm -v "${WORKSPACE}":/ws -w /ws python:3.11-slim bash -c "
            python -m pip install --upgrade pip &&
            pip install -r requirements.txt -r requirements-dev.txt &&
            mkdir -p reports &&
            pytest -q --junitxml=reports/test-results.xml || true
          "
        '''
      }
      post {
        always { junit 'reports/test-results.xml' }
      }
    }

    stage('Build image') {
      steps {
        sh '''
          set -eux
          docker build -t $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT .
        '''
      }
    }

    stage('Push (solo main)') {
      when { branch 'main' }
      steps {
        sh '''
          set -eux
          echo $DOCKERHUB_PSW | docker login $REGISTRY_HOST -u $DOCKERHUB_USR --password-stdin
          docker push $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT
          docker tag  $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT $REGISTRY_HOST/$IMAGE_NAME:latest
          docker push $REGISTRY_HOST/$IMAGE_NAME:latest
        '''
      }
    }

        stage('Deploy (staging locale via docker run)') {
      steps {
        sh '''
          set -eux
          docker rm -f model-api || true
          # usa l’immagine appena buildata (o latest se hai fatto il push)
          docker run -d --name model-api -p 8000:8000 \
            -e MODEL_URL="https://raw.githubusercontent.com/Profession-AI/progetti-devops/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl" \
            -e MODEL_PATH="/app/model/sentiment.pkl" \
            $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT
        '''
      }
    }
  }

  post {
    success { echo '✅ Pipeline ok' }
    failure { echo '❌ Pipeline failed' }
  }
}
