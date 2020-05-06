FROM kbase/kbase:sdkbase2.latest

# install cython that pysam likes
RUN apt-get update && apt-get install -y build-essential wget
RUN pip install --upgrade pip setuptools Cython==0.25

###### CheckM installation
#  Directions from https://github.com/Ecogenomics/CheckM/wiki/Installation#how-to-install-checkm

# CheckM requires the following programs to be added to your system path:
#
# HMMER (>=3.1b1)
# prodigal (2.60 or >=2.6.1)
# executable must be named prodigal and not prodigal.linux
# pplacer (>=1.1)
# guppy, which is part of the pplacer package, must also be on your system path
# pplacer binaries can be found on the pplacer GitHub page

# Install HMMER (>=3.1b1)
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


# Install Prodigal (2.60 or >=2.6.1)
WORKDIR /kb/module
RUN \
  wget https://github.com/hyattpd/Prodigal/archive/v2.6.3.tar.gz && \
  tar -zxvf v2.6.3.tar.gz && \
  ln -s Prodigal-2.6.3 prodigal && \
  rm -f v2.6.3.tar.gz && \
  cd prodigal && \
  make && \
  cp prodigal /kb/deployment/bin/prodigal

# Install Pplacer (>=1.1)
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
# Until seeing "Successfully installed ScreamingBackpack-0.2.333 checkm-genome-1.0.8 dendropy-4.2.0 pysam-0.10.0"
WORKDIR /kb/module

RUN \
  pip install pysam numpy checkm-genome==1.0.18 \
  && cp -R /usr/local/bin/checkm /kb/deployment/bin/CheckMBin

# For checkm-genome required data
RUN \
    mkdir -p /data/checkm_data \
    && mv /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG.orig \
    && touch /data/DATA_CONFIG && \
    && cp /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG.orig /data/DATA_CONFIG \
    && ln -sf /data/DATA_CONFIG /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG \
    && chmod +rwx /data/DATA_CONFIG

COPY ./ /kb/module

WORKDIR /kb/module

RUN mkdir -p /kb/module/work \
    && chmod -R a+rw /kb/module \
    && make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
