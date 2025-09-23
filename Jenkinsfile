pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }

  environment {
    IMAGE_NAME    = 'sentiment-api'
    REGISTRY_HOST = credentials('docker-registry-url')   // es: docker.io  (Secret text)
    REGISTRY_NS   = 'matteoferrillo'                     // <--- CAMBIA se diverso
    IMAGE_REPO    = "${REGISTRY_HOST}/${REGISTRY_NS}/${IMAGE_NAME}"
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

    // Esegue i test in un container Python, così non servono Python/pip sulla macchina Jenkins
    stage('Test (container python)') {
      steps {
        sh '''
          docker run --rm -v "$PWD":/ws -w /ws python:3.11-slim bash -lc "
            python -m pip install --upgrade pip &&
            pip install -r requirements.txt -r requirements-dev.txt &&
            pytest -q --junitxml=reports/test-results.xml
          "
        '''
      }
      post { always { junit 'reports/test-results.xml' } }
    }

    stage('Build image') {
      steps {
        sh 'docker build -t $IMAGE_REPO:$GIT_COMMIT .'
      }
    }

    // Push solo su branch main
    stage('Push (main only)') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'docker-registry-creds',    // Username+Password/Token (RW) su Docker Hub
          usernameVariable: 'USR',
          passwordVariable: 'PSW'
        )]) {
          sh '''
            echo "$PSW" | docker login "$REGISTRY_HOST" -u "$USR" --password-stdin
            docker push "$IMAGE_REPO:$GIT_COMMIT"
            docker tag  "$IMAGE_REPO:$GIT_COMMIT" "$IMAGE_REPO:latest"
            docker push "$IMAGE_REPO:latest"
          '''
        }
      }
    }

    // Deploy di STAGING locale (porta 18000) usando l'immagine appena buildata
    stage('Deploy (staging locale)') {
      steps {
        sh '''
          docker rm -f sentiment-api-ci || true
          docker run -d --name sentiment-api-ci -p 18000:8000 "$IMAGE_REPO:$GIT_COMMIT"
        '''
      }
    }
  }

  post {
    success { echo '✅ Test, Build, Push (se main) e Deploy di staging completati' }
    failure { echo '❌ Pipeline failed' }
  }
}
