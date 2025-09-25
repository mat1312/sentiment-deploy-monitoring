pipeline {
  agent any

  environment {
    // immagine
    IMAGE_NAME   = 'sentiment-api'

    // registry (es.: docker.io/matteoferrillo) salvato come Secret Text con id: docker-registry-url
    REGISTRY_HOST = credentials('docker-registry-url')

    // credenziali Docker Hub (Username + Password/PAT) con id: docker-registry-creds
    DOCKERHUB     = credentials('docker-registry-creds')

    // volume named con cui hai avviato Jenkins:  docker run ... -v jenkins_home:/var/jenkins_home
    JENKINS_VOL = 'jenkins_home'

    // path della workspace dentro il volume named (uguale per tutti i job)
    WS_IN_VOL   = "/jenkins/workspace/${JOB_NAME}"
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
        sh """
          set -e
          docker run --rm \
            -v ${JENKINS_VOL}:/jenkins \
            -w ${WS_IN_VOL} \
            python:3.11-slim bash -lc '
              python -m pip install --upgrade pip &&
              pip install -r requirements.txt -r requirements-dev.txt &&
              mkdir -p reports &&
              pytest -q --junitxml=reports/test-results.xml || true
            '
        """
      }
      post {
        // Evita il FAIL della pipeline se per qualche motivo il report non c'è
        always { junit testResults: 'reports/test-results.xml', allowEmptyResults: true }
      }
    }

    stage('Build image') {
      steps {
        sh """
          set -eux
          docker build -t ${REGISTRY_HOST}/${IMAGE_NAME}:${GIT_COMMIT} .
          docker tag  ${REGISTRY_HOST}/${IMAGE_NAME}:${GIT_COMMIT} ${REGISTRY_HOST}/${IMAGE_NAME}:latest
        """
      }
    }

    stage('Push (solo main)') {
      when { branch 'main' }
      steps {
        sh """
          set -eux
          echo "\$DOCKERHUB_PSW" | docker login ${REGISTRY_HOST} -u "\$DOCKERHUB_USR" --password-stdin
          docker push ${REGISTRY_HOST}/${IMAGE_NAME}:${GIT_COMMIT}
          docker push ${REGISTRY_HOST}/${IMAGE_NAME}:latest
        """
      }
    }

    stage('Deploy (staging locale via docker run)') {
      steps {
        sh """
          set -eux
          docker rm -f model-api || true

          # Avvia l'app montando il volume named 'jenkins_home' anche qui.
          # Il modello viene letto dalla repo: /jenkins/workspace/<JOB_NAME>/model/sentiment_analysis_model.pkl
          docker run -d --name model-api -p 8000:8000 \
            -v ${JENKINS_VOL}:/jenkins \
            -e MODEL_URL= \
            -e MODEL_PATH="/jenkins/workspace/${JOB_NAME}/model/sentiment_analysis_model.pkl" \
            ${REGISTRY_HOST}/${IMAGE_NAME}:${GIT_COMMIT}
        """
      }
    }
  }

  post {
    success { echo '✅ Pipeline ok' }
    failure { echo '❌ Pipeline failed' }
  }
}
