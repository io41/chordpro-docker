FROM ubuntu:rolling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y chordpro
ENTRYPOINT ["chordpro"]
