FROM maven:3-jdk-8

RUN apt-get update
RUN apt-get install -y python3 python3-pip git

RUN useradd -rm -d /home/jdbl -s /bin/bash -G sudo -u 8877 jdbl
USER jdbl

WORKDIR /home/jdbl

ARG LIB_VER=unknown
RUN git clone https://github.com/castor-software/jdbl.git
RUN cd jdbl; git checkout yajta_integration; mvn install -Dmaven.test.skip;
RUN cd ..;

COPY requirements.txt requirements.txt
RUN pip3 install --requirement requirements.txt 

RUN mkdir results
ENV M2_HOME=/home/jdbl/.m2/
ENV GITHUB_OAUTH=''

COPY coverageAgent.jar coverageAgent.jar
COPY __init__.py /__init__.py
COPY jdbl.py jdbl.py
COPY core core


ENTRYPOINT [ "./jdbl.py" ]