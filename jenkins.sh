#!/bin/bash
# Script for the Jenkins build system

while [ "$1" != "" ]; do 
    case $1 in
        --build )
            INSTALL_LIB_DIR=$JENKINS_HOME/usr/local/lib \
                INSTALL_INC_DIR=$JENKINS_HOME/usr/local/include \
                NVCC=/usr/local/cuda-6.5/bin/nvcc make -j
            ;;
        --test )
            cd test;
            python *.py
            ;;
        * )
            exit 1
    esac
    shift
done
