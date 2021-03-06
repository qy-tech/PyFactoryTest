#!/bin/bash
export DISPLAY=:0.0

sleep 1

EXECUTABLE=/tmp/FactoryTest

CONFIGFILE=/tmp/config.yaml

LOGFILE=/tmp/factory_test_log.txt

UDISK=/media/root/UDisk/

# mount udisk to specify directory
mount /dev/$1 $UDISK

echo "udisk add /dev/$1 mount $UDISK" >$LOGFILE

factoryTest="$UDISK/FactoryTest"

config="$UDISK/config.yaml"

echo "FactoryTest bin path $factoryTest" >>$LOGFILE

# check if config exist and copy config file to /tmp directory
if [ -e "$config" ]; then
    echo "copy config file " >>$LOGFILE

    cp $config $CONFIGFILE
fi

# check if test bin file exist and copy test bin file to /tmp directory
if [ -e "$factoryTest" ]; then
    echo "copy FactoryTest bin " >>$LOGFILE

    cp $factoryTest $EXECUTABLE

    # modify factory bin file permission to execute
    if [ -e $EXECUTABLE ]; then
        echo "run FactoryTest bin file" >>$LOGFILE

        chmod 777 $EXECUTABLE

        $EXECUTABLE
    fi
fi

# umount dev and remove directory
umount /dev/$1

if [ $? -eq 0 ]; then
    rm -rf $UDISK
fi
