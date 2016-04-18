#!/bin/bash

VERSION="0.7"
DOCKER_VERSION="1.9.1"

control_version() {
    if [[ ${PRINT_VERSION} == YES ]];then
        echo hive:   ${VERSION}
        echo docker: ${DOCKER_VERSION}
        exit 0
    fi
}

usage() {
    echo "Pre Hive container options:"
    echo "==========================="
    echo "usage: ${0} [option] [Hive Container Options and Parameters]"
    echo "  -i, --init               init docker-toolbox for local_cluster"
    echo "  -u, --update             update to the REQUESTED_VERSION defined in the ${0} script"
    echo "  -t, --no-tty             remove tty for the hive instance"
    echo "  -v, --verbose            verbose"
    echo "  -c, --clean              stop running containers, remove all containers and image without tag"
    echo "  -d, --docker             give the docker version you want to use in hive"
    echo "  -h, --help               show this help message and exit"
    echo "  --version                print the script version and exit"
    echo " "
}

verbose() {
    if [[ ${VERBOSE} == YES ]]
    then echo -e "\e[36mhive-bash: $1\e[39m"; fi
}

clean_containers() {
    verbose "Stopping running container(s)"
    running_containers=$(docker ps -q)
    if [[ ${running_containers} != "" ]];then
        docker kill ${running_containers}
    fi
    verbose "Deleting all container(s)"
    stopped_containers=$(docker ps -qa)
    if [[ ${stopped_containers} != "" ]];then
        docker rm ${stopped_containers}
    fi
    verbose "Deleting image without tag"
    untagged_container=$(docker images -q -f dangling=true)
    if [[ ${untagged_container} != "" ]];then
        docker rmi ${untagged_container}
    fi
}

clean() {
    if [[ ${CLEAN} == YES ]];then
        clean_containers
        exit 0
    fi
}

copy_data_to_hive_working_directory() {
    # HOST IS A CONTAINER
    verbose "Parent is a container"
    ubuntuContainer="ubuntu:14.04.2"
    hive_working_directory="hive_working_directory"
    container="hive_working_directory_to_volume"

    # LOOK IF DATA ARE COPIED
    docker run                                                  \
        -v ${hive_working_directory}:/${hive_working_directory} \
        ${ubuntuContainer}                                      \
        bash -c "if [[ ! -d /hive_working_directory/.hive ]];then exit 1;fi"

    if [[ $? != 0 ]];then
        verbose "folder .hive does not exist"
        echo "Copying current directory to a volume (avoid to run hive on big directory ; copy is only done once)"
        docker run -d                                               \
            -v ${hive_working_directory}:/${hive_working_directory} \
            ${ubuntuContainer}                                      \
            bash -c "while true; do echo ping; sleep 60; done"      \
            > container_id
        mkdir -p .hive
        docker cp . $(cat container_id):/${hive_working_directory}
        rm -r .hive

        # REMOVE TEMP_CONTAINER
        docker stop $(cat container_id) > /dev/null
        docker rm $(cat container_id) > /dev/null
        rm container_id
    else
        verbose "folder .hive exist, don't copy code to a volume"
    fi
}

print_help () {
    if [[ ${HELP} == YES && ${ARGS} == "" ]];then
        usage
        echo " "
        echo "Hive Container options and Parameters:"
        echo "======================================"
        ARGS="-h"
    fi
}

init_vm_for_local_cluster () {
    if [[ ${INIT_CLUSTER} == YES ]];then
        docker-machine ssh default "sudo mkdir -p /var/lib/kubelet"
        docker-machine ssh default "sudo mount --bind /var/lib/kubelet /var/lib/kubelet"
        docker-machine ssh default "sudo mount --make-shared /var/lib/kubelet"
        echo "the default machine is now ready for a local-kubernetes-cluster"
    fi
}

start_hive() {
    docker run -i ${TTY}                              \
        --net=host                                    \
        -v hive_docker:/root/.docker                  \
        -v hive_log:/hive_log                         \
        -v hive_share:/hive_share                     \
        -v //var/run/docker.sock:/var/run/docker.sock \
        ${container_or_host}                          \
        ${hive_container} ${ARGS}
}

main() {
    
    # CONTROL PARAMETERS
    for i in "${@}"; do
    case ${i} in
        -i|--init)              INIT_CLUSTER=YES;             shift 1;;
        -u|--update)            UPDATE=YES;                   shift 1;;
        -t|--no-tty)            NOTTY=YES;                    shift 1;;
        -v|--verbose)           VERBOSE=YES;                  shift 1;;
        -c|--clean)             CLEAN=YES;                    shift 1;;
        -w|--rm-hive-directory) REMOVE_WORKING_DIRECTORY=YES; shift 1;;
        -d=*|--docker=*)        DOCKER_VERSION="${i#*=}";     shift 1;;
        -h|--help)              HELP=YES;                     shift 1;;
        --version)              PRINT_VERSION=YES;            shift 1;;
        -*) echo "unknown option: ${i}" >&2; usage;           exit 1;;
        *)                      ARGS="$@";                    break;;
    esac
    done

    hive_container="tdeheurles/hive:${VERSION}--docker${DOCKER_VERSION}"

    verbose "Start:"
    control_version
    clean 
    init_vm_for_local_cluster

    if [[ -f /.dockerenv ]];then
        copy_data_to_hive_working_directory
        
        container_or_host="-v ${hive_working_directory}:/${hive_working_directory}"
        container_or_host+=" -e HIVE_HOME=/${hive_working_directory}"
    else
        # RUNNING FROM A BAREMETAL OR A VIRTUAL MACHINE (NOT A CONTAINER)
        verbose "Parent is host"
        container_or_host="-v /$(pwd):/$(pwd)"
        container_or_host+=" -e HIVE_HOME=/$(pwd)"
    fi

    TTY=""
    if [[ ${NOTTY} != YES ]];then TTY="-t"; fi

    print_help
    start_hive
}
