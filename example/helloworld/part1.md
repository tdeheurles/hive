# A simple HIVE example

#### In this tutorial, you will
- install docker. The only pre-requisite
- write a really simple helloworld web server
- dockerise that webserver
- build and run it locally
- generate most of the devops part by using hive templates
- push the docker image to docker hub
- start a gcloud kubernetes cluster
- deploy our web server to kubernetes

#### Note to Windows users
This project generate lots of code that will run under linux environment and are sensitive to `LF` line endings. 
In order to ask your git to not update `LF` to `CRLF`, run `git config --global core.autocrlf false` before cloning the repository. Then run `git config --global core.autocrlf true` to have the previous behavior. 

#### pre-requisite
Install docker from [this page](https://docs.docker.com/engine/installation/) by choosing your environment. Confirm that everything is fine by following the docker helloworld at the end of installation.

#### Create our project
When you're done, move to the [create project page](part2.md).

