FROM perl:buster
RUN apt-get update \
    && cpan install chordpro
ENTRYPOINT ["chordpro"]