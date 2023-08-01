FROM p4lang/behavioral-model:latest
LABEL maintainer="Antonin Bas <antonin@barefootnetworks.com>"
LABEL description="This Docker image does not have any dependency on PI or P4 \
Runtime, it only builds bmv2 simple_switch."

RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8 
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y git \
    rsyslog \
    iputils-ping \
    inetutils-traceroute \
    net-tools \
    tcpdump \
    dnsutils \
    build-essential \
    iperf3 \
    ethtool \
    iptables \
    mininet \
    help2man \
    git \ 
    python3-pip \
    curl

RUN . /etc/os-release && echo "deb https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/ /" | tee /etc/apt/sources.list.d/home:p4lang.list &&  curl -L "https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/Release.key" | apt-key add - && apt-get update && apt install p4lang-p4c -y

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y -q openssh-server

WORKDIR /

COPY docker-start /usr/sbin/docker-start
RUN chmod +x /usr/sbin/docker-start
ENTRYPOINT ["/usr/sbin/docker-start"]
