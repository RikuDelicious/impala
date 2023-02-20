#!/bin/bash
echo "@start docker-web-run-test.sh"

echo "### python manage.py migrate --settings impala.settings_devcontainer"
python manage.py migrate --settings impala.settings.devcontainer

echo "### sudo apt update"
sudo apt-get update && sudo apt-get install -y curl jq

echo "### waiting for localstack init ready stage completed..."
function check_ready_completed () {
    while true
    do
        result=`curl -s localstack:4566/_localstack/init/ready | jq ".completed"`
        echo $result
        if [ $result = "true" ]; then
            break
        fi
        sleep 0.5
    done
}
# 関数check_ready_completedを子プロセスで実行する
export -f check_ready_completed
timeout 60s bash -c check_ready_completed
if [ $? -eq 0 ]; then
    echo "### pytest --ds=impala.settings.devcontainer"
    pytest --ds=impala.settings.devcontainer
else
    echo "### [ERROR] localstack health check timed out and test was not run."
fi

echo "@end docker-web-run-test.sh"