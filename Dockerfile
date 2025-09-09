FROM kbase/sdkpython:3.8.10
LABEL maintainer="KBase Developer"

# --- system tools (for downloads / archives) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget unzip ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# Ensure conda python bin first on PATH in this image family
ENV PATH="/opt/conda3/bin:${PATH}"

# --- HMMER (>=3.1b1); keep 3.1b2 like the original image did ---
WORKDIR /opt
RUN wget -q http://eddylab.org/software/hmmer3/3.1b2/hmmer-3.1b2-linux-intel-x86_64.tar.gz \
 && tar -xzf hmmer-3.1b2-linux-intel-x86_64.tar.gz \
 && rm -f hmmer-3.1b2-linux-intel-x86_64.tar.gz \
 && cd hmmer-3.1b2-linux-intel-x86_64 \
 && ./configure && make && make install

# --- Prodigal 2.6.3 ---
RUN wget -q https://github.com/hyattpd/Prodigal/archive/v2.6.3.tar.gz \
 && tar -xzf v2.6.3.tar.gz && rm -f v2.6.3.tar.gz \
 && cd Prodigal-2.6.3 && make \
 && install -m 0755 prodigal /usr/local/bin/prodigal

# --- pplacer 1.1.alpha19 (includes guppy) ---
RUN wget -q https://github.com/matsen/pplacer/releases/download/v1.1.alpha19/pplacer-linux-v1.1.alpha19.zip \
 && unzip -q pplacer-linux-v1.1.alpha19.zip \
 && rm -f pplacer-linux-v1.1.alpha19.zip \
 && mv pplacer-Linux-v1.1.alpha19 /opt/pplacer \
 && ln -s /opt/pplacer/pplacer /usr/local/bin/pplacer \
 && ln -s /opt/pplacer/guppy   /usr/local/bin/guppy

# --- Python deps + CheckM (current stable) ---
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir numpy scipy pysam dendropy matplotlib \
 && pip install --no-cache-dir "checkm-genome==1.2.3"

# Point CheckM to a writable data root; write DATA_CONFIG in a version-agnostic way
RUN mkdir -p /data/checkm_data && \
 python - <<'PY'
import importlib, pathlib
pkg = importlib.import_module('checkm')
cfg = pathlib.Path(pkg.__file__).parent/'DATA_CONFIG'
cfg.write_text('/data/checkm_data\n')
print('Wrote', cfg, '-> /data/checkm_data')
PY
# seed the root (download happens at runtime)
RUN checkm data setRoot /data/checkm_data || true

# --- app files & build ---
WORKDIR /kb/module
COPY ./ /kb/module

RUN mkdir -p /kb/module/work/tmp/test_data \
 && cp -r /kb/module/test/data/* /kb/module/work/tmp/test_data/ 2>/dev/null || true \
 && chmod -R a+rw /kb/module \
 && make all

ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD []
