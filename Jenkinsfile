pipeline {
  agent any

  environment {
    // ---- IMMAGINE DOCKER ----
    IMAGE_NAME    = 'sentiment-api'

    // ---- REGISTRY ----
    // ID "docker-registry-url" = Secret text con valore tipo: docker.io/matteoferrillo
    REGISTRY_HOST = credentials('docker-registry-url')

    // ID "docker-registry-creds" = Username + Password/Token Docker Hub
    DOCKERHUB     = credentials('docker-registry-creds')

    // ---- Percorsi condivisi (volume jenkins_home) ----
    // Il volume locale usato quando si è lanciato Jenkins:  -v jenkins_home:/var/jenkins_home
    JENKINS_VOL   = 'jenkins_home'

    // ---- Modello (fallback URL pubblico) ----
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
        // WS_IN_VOL = /jenkins/workspace/<JOB_NAME>
        // PYTHONPATH puntato alla root del repo per permettere "from app.main import app"
        sh '''
          set -e
          WS_IN_VOL="/jenkins/workspace/$JOB_NAME"

          docker run --rm \
            -v ${JENKINS_VOL}:/jenkins \
            -w "$WS_IN_VOL" \
            -e PYTHONPATH="$WS_IN_VOL" \
            python:3.11-slim bash -lc '
              python -m pip install --upgrade pip &&
              pip install -r requirements.txt -r requirements-dev.txt &&
              mkdir -p reports &&
              pytest -q --junitxml=reports/test-results.xml
            '
        '''
      }
      post {
        // Pubblica i risultati test; il build diventa UNSTABLE/FAILED se i test falliscono
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
          WS_IN_VOL="/jenkins/workspace/$JOB_NAME"

          # Riavvia il container locale di staging
          docker rm -f model-api || true

          docker run -d --name model-api -p 8000:8000 \
            -v ${JENKINS_VOL}:/jenkins \
            -e MODEL_URL="$MODEL_URL" \
            -e MODEL_PATH="$WS_IN_VOL/model/sentiment_analysis_model.pkl" \
            $REGISTRY_HOST/$IMAGE_NAME:$GIT_COMMIT
        '''
      }
    }
  }

  post {
    success { echo '✅ Pipeline OK' }
    unstable { echo '🟡 Pipeline UNSTABLE (verifica i test)' }
    failure { echo '❌ Pipeline FAILED' }
  }
}
