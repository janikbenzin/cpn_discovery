#!/bin/sh

###
## ProM specific
###
PROGRAM=ProM
CP=./corradinietal/colliery_source.jar
LIBDIR=./corradinietal/lib
MAIN=it.unicam.pros.colliery.Colliery

####
## Environment options
###
JAVA=/usr/lib/jvm/java-21-openjdk-21.0.1.0.12-4.rolling.fc39.x86_64/bin/java

###
## Main program
###

add() {
  CP=${CP}:$1
}


for lib in $LIBDIR/*.jar
do
  add $lib
done

echo $JAVA -Xmx4G -classpath ${CP} -Djava.library.path=${LIBDIR} ${MAIN} $@
$JAVA -Xmx4G -classpath ${CP} -Djava.library.path=${LIBDIR} ${MAIN} $@

