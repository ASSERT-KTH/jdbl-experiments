FROM maven:3-jdk-8

RUN apt-get update
RUN apt-get install -y python3 python3-pip git

ARG USER_ID
ARG GROUP_ID

RUN groupadd -r --gid $GROUP_ID jdbl; exit 0
RUN useradd -rm -d /home/jdbl -s /bin/bash -G sudo --uid $USER_ID --gid $GROUP_ID jdbl
USER jdbl

WORKDIR /home/jdbl

ARG LIB_VER
RUN git clone https://github.com/castor-software/jdbl.git
RUN cd jdbl;  git checkout $LIB_VER;
RUN cd jdbl;  mvn install -Dmaven.test.skip;

COPY requirements.txt requirements.txt
RUN pip3 install --requirement requirements.txt 

RUN mkdir results
ENV M2_HOME=/usr/share/maven
ENV GITHUB_OAUTH=''

COPY coverageAgent.jar coverageAgent.jar
COPY extractclassusage.jar extractclassusage.jar
COPY __init__.py /__init__.py
COPY jdbl.py jdbl.py
COPY main.py main.py
COPY compile.py compile.py
COPY usage.py usage.py
COPY verify.py verify.py
COPY core core


ENTRYPOINT [ "./main.py" ]