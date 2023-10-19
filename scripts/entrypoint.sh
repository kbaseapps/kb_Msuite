#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
elif [ ! -z ${KBASE_TEST_TOKEN} ] ; then
  # put the test token into work/token
  cat <<< ${KBASE_TEST_TOKEN} > ./work/token
  export KB_AUTH_TOKEN=${KBASE_TEST_TOKEN}
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cp /miniconda/lib/python3.6/site-packages/checkm/DATA_CONFIG.orig /data/checkm1/DATA_CONFIG
  mkdir -p /data/checkm1/checkm_data
  cd /data/checkm1/checkm_data
  if [ -d "/data/checkm1/checkm_data/genome_tree" ] ; then
    echo "already have CheckM1 data"
  else
    echo "downloading CheckM1 data: https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz"
    if [ -e /kb/module/checkm_data_2015_01_16.tar.gz ] ; then
      cp /kb/module/checkm_data_2015_01_16.tar.gz .
    else
      wget -q https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz
    fi
    tar -xzf checkm_data_2015_01_16.tar.gz
    rm -r checkm_data_2015_01_16.tar.gz
  fi
  echo /data/checkm1/checkm_data | checkm data setRoot /data/checkm1/checkm_data
  cd /data/checkm2
  if [ -s "/data/checkm2/CheckM2_database/uniref100.KO.1.dmnd" ] ; then
    echo "already have CheckM2 data"
  else
    echo "downloading CheckM2 data: uniref100.KO.1.dmnd from https://zenodo.org/api/files/fd3bc532-cd84-4907-b078-2e05a1e46803/checkm2_database.tar.gz"
    checkm2 database --download --path /data/checkm2
  fi
  export CHECKM2DB="/data/checkm2/CheckM2_database/uniref100.KO.1.dmnd"
  cd /kb/module
  if [ -d "/data/checkm1/checkm_data/genome_tree" -a -s "/data/checkm2/CheckM2_database/uniref100.KO.1.dmnd" ] ; then
    touch /data/__READY__
  else
    echo "Init failed"
  fi
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
