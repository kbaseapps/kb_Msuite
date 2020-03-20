FROM kbase/sdkbase2:python
MAINTAINER KBase Developer

# install cython that pysam likes
RUN apt-get update && apt-get install -y build-essential wget
RUN pip install --upgrade pip setuptools Cython==0.25


###### CheckM installation
# Directions available here: https://github.com/Ecogenomics/CheckM/wiki/Installation#how-to-install-checkm

# Now install CheckM, but not data

# Install HMMER
WORKDIR /kb/module
RUN \
  curl http://eddylab.org/software/hmmer3/3.1b2/hmmer-3.1b2-linux-intel-x86_64.tar.gz > hmmer-3.1b2-linux-intel-x86_64.tar.gz && \
  tar -zxvf hmmer-3.1b2-linux-intel-x86_64.tar.gz && \
  ln -s hmmer-3.1b2-linux-intel-x86_64 hmmer && \
  rm -f hmmer-3.1b2-linux-intel-x86_64.tar.gz && \
  cd hmmer && \
  ./configure && \
  make && make install && \
  cd easel && make check && make install


# Install Prodigal
WORKDIR /kb/module
RUN \
  wget https://github.com/hyattpd/Prodigal/archive/v2.6.3.tar.gz && \
  tar -zxvf v2.6.3.tar.gz && \
  ln -s Prodigal-2.6.3 prodigal && \
  rm -f v2.6.3.tar.gz && \
  cd prodigal && \
  make && \
  cp prodigal /kb/deployment/bin/prodigal

#ENV PATH "$PATH:/kb/development/bin/prodigal"


WORKDIR /kb/module
RUN \
  wget https://github.com/matsen/pplacer/releases/download/v1.1.alpha19/pplacer-linux-v1.1.alpha19.zip && \
  unzip pplacer-linux-v1.1.alpha19.zip && \
  ln -s pplacer-Linux-v1.1.alpha19 pplacer && \
  rm -f pplacer-linux-v1.1.alpha19.zip && \
  rm -f pplacer-1.1.alpha19.tar.gz && \
  cp -R pplacer-Linux-v1.1.alpha19 /kb/deployment/bin/pplacer

ENV PATH "$PATH:/kb/deployment/bin/pplacer"


# Install CheckM (collected packages: checkm-genome, pysam, dendropy, ScreamingBackpack)
WORKDIR /kb/module

# Pysam installation failing with pip, but working with pip3
#  pip install pysam \
RUN \
  pip install pysam numpy \
  && pip install checkm-genome==1.1.2 \
  && cp -R /miniconda/bin/checkm /kb/deployment/bin/CheckMBin

# For checkm-genome required data
RUN \
  mkdir /data && \
  mv /miniconda/lib/python3.6/site-packages/checkm/DATA_CONFIG /miniconda/lib/python3.6/site-packages/checkm/DATA_CONFIG.orig && \
  touch /data/DATA_CONFIG && \
  cp /miniconda/lib/python3.6/site-packages/checkm/DATA_CONFIG.orig /data/DATA_CONFIG && \
  ln -sf /data/DATA_CONFIG /miniconda/lib/python3.6/site-packages/checkm/DATA_CONFIG && \
  mkdir -p /data/checkm_data

# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
