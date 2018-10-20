if [ "${1}" == "install" ]; then
    curl -L https://raw.githubusercontent.com/OriHoch/travis-ci-operator/master/travis_ci_operator.sh \
        > $HOME/bin/travis_ci_operator.sh &&\
    bash $HOME/bin/travis_ci_operator.sh init &&\
    travis_ci_operator.sh docker-login

elif [ "${1}" == "script" ]; then
    docker build -t ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:${TRAVIS_COMMIT} .

elif [ "${1}" == "deploy" ]; then
    if [ "${TRAVIS_BRANCH}" == "master" ] &&\
       [ "${TRAVIS_TAG}" == "" ] &&\
       [ "${TRAVIS_PULL_REQUEST}" == "false" ]
    then
        docker push ${DOCKER_IMAGE}:latest &&\
        docker push ${DOCKER_IMAGE}:${TRAVIS_COMMIT} &&\
        travis_ci_operator.sh github-yaml-update \
            migdar-k8s master values.auto-updated.yaml '{"internal-search-ui":{"backendImage": "'${DOCKER_IMAGE}:${TRAVIS_COMMIT}'"}}' \
            "automatic update of internal-search-ui backend" OriHoch/migdar-k8s &&\
        echo &&\
        echo Great Success &&\
        echo &&\
        echo ${DOCKER_IMAGE}:latest &&\
        echo ${DOCKER_IMAGE}:${TRAVIS_COMMIT}
    else
        echo Skipping deployment
    fi

fi
