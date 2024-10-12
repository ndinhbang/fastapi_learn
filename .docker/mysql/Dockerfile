FROM mysql:8.0.37 AS builder

ARG MYSQL_ROOT_PASSWORD

# That file does the DB initialization but also runs mysql daemon, by removing the last line it will only init
RUN ["sed", "-i", "s/exec \"$@\"/echo \"not running $@\"/", "/usr/local/bin/docker-entrypoint.sh"]

# needed for intialization
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

COPY init.sql /docker-entrypoint-initdb.d/

# Need to change the datadir to something else that /var/lib/mysql because the parent docker file defines it as a volume.
# https://docs.docker.com/engine/reference/builder/#volume :
#       Changing the volume from within the Dockerfile: If any build steps change the data within the volume after
#       it has been declared, those changes will be discarded.
RUN ["/usr/local/bin/docker-entrypoint.sh", "mysqld", "--datadir", "/init-db"]

FROM mysql:8.0.37

COPY --from=builder /init-db /var/lib/mysql
COPY my.cnf /etc/mysql/conf.d/my.cnf