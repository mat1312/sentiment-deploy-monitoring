FROM jenkins/jenkins:lts-jdk17
RUN jenkins-plugin-cli --plugins workflow-aggregator git credentials-binding ssh-agent timestamper ansicolor junit
