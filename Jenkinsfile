pipeline {
  agent any

  environment {
    IMAGE_NAME    = 'sentiment-api'

    // Credenziali/registry
    REGISTRY_HOST = credentials('docker-registry-url')      // es: docker.io/matteoferrillo
    DOCKERHUB     = credentials('docker-registry-creds')    // user/token Docker Hub

    // Volume della home di Jenkins (come da run: -v jenkins_home:/var/jenkins_home)
    JENKINS_VOL   = 'jenkins_home'

    // Modello pubblico (fallback)
    MODEL_URL     = 'https://raw.githubusercontent.com/Profession-AI/progetti-devops/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl'
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
          WS_IN_VOL="/jenkins/workspace/$JOB_NAME"
          MODEL_PATH_IN_WS="$WS_IN_VOL/model/sentiment_analysis_model.pkl"

          docker run --rm \
            -v ${JENKINS_VOL}:/jenkins \
            -w "$WS_IN_VOL" \
            -e PYTHONPATH="$WS_IN_VOL" \
            -e MODEL_PATH="$MODEL_PATH_IN_WS" \
            -e MODEL_URL="$MODEL_URL" \
            python:3.11-slim bash -lc '
              set -e
              python -m pip install --upgrade pip
              pip install -r requirements.txt -r requirements-dev.txt
              # Se il file modello non c’è, scaricalo
              test -f "$MODEL_PATH" || { mkdir -p "$(dirname "$MODEL_PATH")"; apt-get update && apt-get install -y curl && curl -L "$MODEL_URL" -o "$MODEL_PATH"; }
              mkdir -p reports
              pytest -q --junitxml=reports/test-results.xml
            '
        '''
      }
      post {
        always { junit testResults: 'reports/test-results.xml', allowEmptyResults: false }
      }
    }

    stage('Build image') {
      steps {
        sh '''
          set -eux
          docker build -t $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT .
          docker tag  $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT $REGISTRY_HOST/$IMAGE_NAME:latest
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
          docker push $REGISTRY_HOST/$IMAGE_NAME:latest
        '''
      }
    }

    stage('Deploy (staging locale via docker run)') {
      steps {
        sh '''
          set -eux
          docker rm -f model-api || true

          # In deploy useremo il download da MODEL_URL; non montiamo la workspace.
          docker run -d --name model-api -p 8000:8000 \
            -e MODEL_URL="$MODEL_URL" \
            -e MODEL_PATH="/app/model/sentiment.pkl" \
            $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT
        '''
      }
    }
  }

  post {
    success  { echo '✅ Pipeline OK' }
    unstable { echo '🟡 Pipeline UNSTABLE (verifica i test)' }
    failure  { echo '❌ Pipeline FAILED' }
  }
}
