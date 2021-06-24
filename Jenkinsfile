pipeline {
  agent any

  environment {
        GIT_NAME = "copernicus-insitu-db"
        SONARQUBE_TAGS = "cis2.eea.europa.eu"
        CSSLINT_PARAMS = "--exclude-list=copernicus-insitu-db/insitu/static/css/animate.css,copernicus-insitu-db/insitu/static/css/bootstrap-datetime-picker.min.css,copernicus-insitu-db/insitu/static/css/bootstrap-theme.min.css,copernicus-insitu-db/insitu/static/css/bootstrap.min.css,copernicus-insitu-db/insitu/static/css/buttons.dataTables.min.css,copernicus-insitu-db/insitu/static/css/codemirror.min.css,copernicus-insitu-db/insitu/static/css/jquery.dataTables.min.css,copernicus-insitu-db/insitu/static/css/pivot.min.css,copernicus-insitu-db/insitu/static/css/select2-bootstrap.min.css,copernicus-insitu-db/insitu/static/css/select2.min.css"
    }

  stages {

    stage('Cosmetics') {
      steps {
        parallel(

          "JS Hint": {
            node(label: 'docker') {
              script {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                  sh '''docker run -i --rm --name="$BUILD_TAG-jshint" -e PARAMS="$JSHINT_PARAMS" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/jshint --exclude-path copernicus-insitu-db/.jshintignore'''
                }
              }
            }
          },

          "CSS Lint": {
            node(label: 'docker') {
              script {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                  sh '''docker run -i --rm --name="$BUILD_TAG-csslint" -e PARAMS="$CSSLINT_PARAMS" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/csslint'''
                }
              }
            }
          },

          "PEP8": {
            node(label: 'docker') {
              script {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                  sh '''docker run -i --rm --name="$BUILD_TAG-pep8" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/pep8 --max-line-length=120 --ignore=W503,E203 /code'''
                }
              }
            }
          },

          // "PyLint": {
          //   node(label: 'docker') {
          //     script {
          //       catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          //         sh '''docker run -i --rm --name="$BUILD_TAG-pylint" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/pylint'''
          //       }
          //     }
          //   }
          // }

        )
      }
    }

    stage('Code') {
      steps {
        parallel(

          // "JS Lint": {
          //   node(label: 'docker') {
          //     sh '''docker run -i --rm --name="$BUILD_TAG-jslint" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/jslint4java'''
          //   }
          // },

          // "Flake8": {
          //   node(label: 'docker') {
          //     sh '''docker run -i --rm --name="$BUILD_TAG-flake8" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/flake8'''
          //   }
          // },
          "ZPT Lint": {
            node(label: 'docker') {
              sh '''docker run -i --rm --name="$BUILD_TAG-zptlint" -e GIT_BRANCH="$BRANCH_NAME" -e ADDONS="$GIT_NAME" -e DEVELOP="src/$GIT_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/plone-test:4 zptlint'''
            }
          },

          "i18n": {
            node(label: 'docker') {
              sh '''docker run -i --rm --name=$BUILD_TAG-i18n -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/i18ndude'''
            }
          }
        )
      }
    }

    stage('Report to SonarQube') {
      steps {
        node(label: 'swarm') {
          script{
            // get the code
            checkout scm
            // get the result of the tests that were run in a previous Jenkins test
            // get the result of the cobertura test
            // get the sonar-scanner binary location
            def scannerHome = tool 'SonarQubeScanner';
            // get the nodejs binary location
            def nodeJS = tool 'NodeJS11';
            // run with the SonarQube configuration of API and token
            withSonarQubeEnv('Sonarqube') {
                // run sonar scanner
                sh "export PATH=$PATH:${scannerHome}/bin:${nodeJS}/bin; sonar-scanner -Dsonar.python.xunit.skipDetails=true -Dsonar.sources=./eea -Dsonar.projectKey=$GIT_NAME-$BRANCH_NAME -Dsonar.projectVersion=$BRANCH_NAME-$BUILD_NUMBER"
                sh '''try=2; while [ \$try -gt 0 ]; do curl -s -XPOST -u "${SONAR_AUTH_TOKEN}:" "${SONAR_HOST_URL}api/project_tags/set?project=${GIT_NAME}-${BRANCH_NAME}&tags=${SONARQUBE_TAGS},${BRANCH_NAME}" > set_tags_result; if [ \$(grep -ic error set_tags_result ) -eq 0 ]; then try=0; else cat set_tags_result; echo "... Will retry"; sleep 60; try=\$(( \$try - 1 )); fi; done'''
            }
          }
        }
      }
    }

  }

  post {
    changed {
      script {
        def url = "${env.BUILD_URL}/display/redirect"
        def status = currentBuild.currentResult
        def subject = "${status}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
        def summary = "${subject} (${url})"
        def details = """<h1>${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${status}</h1>
                         <p>Check console output at <a href="${url}">${env.JOB_BASE_NAME} - #${env.BUILD_NUMBER}</a></p>
                      """

        def color = '#FFFF00'
        if (status == 'SUCCESS') {
          color = '#00FF00'
        } else if (status == 'FAILURE') {
          color = '#FF0000'
        }

        emailext (subject: '$DEFAULT_SUBJECT', to: '$DEFAULT_RECIPIENTS', body: details)
      }
    }
  }
}
