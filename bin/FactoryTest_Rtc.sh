#!/bin/bash

# 通过RTC更新时间
hwclock -w &>/dev/null
if [ $? -ne 0 ]; then
    echo "RTCTest=[NG]"
    exit 0
fi

sleep 1

hwclock -r &>/dev/null
if [ $? -eq 0 ]; then
    echo "RTCTest=[OK]"
else
    echo "RTCTest=[NG]"
fi
