FROM perl:stable-bookworm
RUN apt-get update
RUN apt-get install -y \
    libpdf-api2-perl \
    libimage-info-perl
RUN cpan install chordpro
ENTRYPOINT ["chordpro"]