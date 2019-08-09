FROM kbase/kbase:sdkbase2.latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN apt-get update

# Here we install a python coverage tool and an
# https library that is out of date in the base image.

RUN pip install coverage

# Hope to solve the "Could not find .egg-info directory in install record for checkm-genome, etc."
RUN pip install --upgrade setuptools pip

# update security libraries in the base image
RUN pip install cffi --upgrade \
    && pip install pyopenssl --upgrade \
    && pip install ndg-httpsclient --upgrade \
    && pip install pyasn1 --upgrade \
    && pip install requests --upgrade \
    && pip install 'requests[security]' --upgrade

###### CheckM installation
#  Directions from https://github.com/Ecogenomics/CheckM/wiki/Installation#how-to-install-checkm
#System requirements
#
#CheckM is designed to run on Linux. The limiting requirement for CheckM is memory. Inference of lineage-specific marker sets using the full reference genome tree required approximately 40 GB of memory. However, a reduced genome tree (--reduced_tree) can also be used to infer lineage-specific marker sets which is suitable for machines with as little as 16 GB of memory. We recommend using the full tree if possible, though our results suggest that the same lineage-specific marker set will be selected for the vast majority of genomes regardless of the underlying reference tree. System requirements are far more modest if you plan to make use of taxonomic-specific marker sets or your own custom marker genes as this bypasses the need to place genomes in the reference genome tree.
#
#How to install CheckM
#
#CheckM requires the following programs to be added to your system path:
#
#HMMER (>=3.1b1)
#prodigal (2.60 or >=2.6.1)
#executable must be named prodigal and not prodigal.linux
#pplacer (>=1.1)
#guppy, which is part of the pplacer package, must also be on your system path
#pplacer binaries can be found on the pplacer GitHub page
#CheckM is a Python 2.x program and we recommend installing it through pip:
#
#> sudo pip install numpy
#> sudo pip install checkm-genome
#
#This will install CheckM and all other required Python libraries.
#
#CheckM relies on a number of precalculated data files. To install these run:
#
#> sudo checkm data update
#
#This will prompt you for an installation directory for the required data files. You can update the data files in the future by re-running this command. If you are unable to automatically download these files (e.g., you are behind a proxy), the files can be manually downloaded from https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz. Decompress this file to an appropriate folder and run checkm data setRoot <data_directory> to inform CheckM of where the files have been placed.
#
#CheckM is now ready to run. For a list of CheckM commands type:
#
#> checkm
#
#If desired, you can also download the latest release of CheckM and install it manually. CheckM makes use of the following Python libraries:
#
#python >= 2.7 and < 3.0
#numpy >= 1.8.0
#scipy >= 0.9.0
#matplotlib >= 1.3.1
#pysam >= 0.8.3
#dendropy >= 4.0.0
#ScreamingBackpack >= 0.2.3

#
#### OK, got that cleared up.  Now install CheckM, but not data
#


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

# Install Pplacer
# NOTE: The following block is replaced by the following section because the need of installing
# opam and its respective dependencies has been a big hassle and unsuccessful
# WORKDIR /kb/module
#RUN \
#  curl -s https://codeload.github.com/matsen/pplacer/tar.gz/v1.1.alpha19 > pplacer-1.1.alpha19.tar.gz && \
#  tar -xvzf pplacer-1.1.alpha19.tar.gz && \
#  ln -s pplacer-1.1.alpha19 pplacer && \
#  rm -f pplacer-1.1.alpha19.tar  && \
#  cd pplacer && \
#  cat opam-requirements.txt | xargs opam install -y && \
#  make all

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
# Until seeing "Successfully installed ScreamingBackpack-0.2.333 checkm-genome-1.0.16 dendropy-4.2.0 pysam-0.10.0"
WORKDIR /kb/module
RUN \
  pip install pysam==0.9 \
  && pip install dendropy \
  && pip install ScreamingBackpack \
  && pip install checkm-genome==1.0.16 \
  && cp -R /usr/local/bin/checkm /kb/deployment/bin/CheckMBin

# For checkm-genome required data
RUN \
    mkdir /data && \
    mv /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG.orig && \
    touch /data/DATA_CONFIG && \
    cp /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG.orig /data/DATA_CONFIG && \
    ln -sf /data/DATA_CONFIG /usr/local/lib/python2.7/dist-packages/checkm/DATA_CONFIG

RUN mkdir -p /data/checkm_data

# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
