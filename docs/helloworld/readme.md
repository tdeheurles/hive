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
If you clone a repository with scripts that are dockerised, remember to add a .gitattributes file to your project
or to config git to not transform the files to CRLF when you checkout.

A bash script with CRLF ending run inside linux (container) will often error by telling that the file doesn't exist. 

You can find information on how to set [git configuration here](https://help.github.com/articles/dealing-with-line-endings/).

#### pre-requisite
Install docker from [this page](https://docs.docker.com/engine/installation/) by choosing your environment.
 
Confirm that everything is fine by following the docker helloworld at the end of installation.

#### Create our project
When you're done, move to the [create project page](part1.md).

