FROM ialarmedalien/kbase_checkm_base:latest

COPY ./ /kb/module

WORKDIR /kb/module

RUN mkdir -p /kb/module/work/tmp/test_data \
    && cp -r /kb/module/test/data/* /kb/module/work/tmp/test_data/ \
    && chmod -R a+rw /kb/module \
    && make all \
    && rm -f /data/__READY__

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
