FROM flink:1.17.0

# Versions
ENV \
  # Apt-Get
  BUILD_ESSENTIAL_VER=12.9ubuntu3 \
  PYTHON_VER=3.10 \
  # PyFlink
  APACHE_FLINK_VER=1.17.0
  
SHELL ["/bin/bash", "-ceuxo", "pipefail"]

RUN apt-get update -y && \
  apt-get install -y --no-install-recommends \
    build-essential=${BUILD_ESSENTIAL_VER} \
    openjdk-11-jdk=11.0.*

# Installing OpenJDK again & setting this is required due to a bug with M1 Macs
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64

RUN apt-get install -y python3.10 python3-dev python3.10-distutils && \
  ln -s /usr/bin/python3.10 /usr/bin/python && \
  wget https://bootstrap.pypa.io/get-pip.py && \
  python get-pip.py && \
  rm get-pip.py && apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  pip3 install --no-cache-dir apache-flink==${APACHE_FLINK_VER} && \
  pip3 cache purge
