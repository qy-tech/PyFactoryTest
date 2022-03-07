#!/bin/bash

result=false
grepInfo=""
writeInfo=""
resultInfo=""

# 判断测试USB还是测试SdCard
if [[ "usb" == "$1" ]]; then
    grepInfo="sd"
    writeInfo="usb test"
    resultInfo="USBTest"
elif [[ "sdcard" == "$1" ]]; then
    grepInfo="mmcblk1"
    writeInfo="sdcard test"
    resultInfo="SdcardTest"
else
    echo "StorageTest=[NG]"
    exit 0
fi

#lsblk -io KNAME,MOUNTPOINT |grep /media/ |grep mmcblk |awk -F/media '{print $2}'
#lsblk -io KNAME,MOUNTPOINT |grep /media/ |grep sd |awk -F/media '{print $2}'
IFS=$'\n'

# 更据lsblk获取U盘或者SD卡的路径,awk -F/media 可以避免默认用空格分割的情况下，外部存储名字可能有空格的问题
# lsblk -io KNAME,MOUNTPOINT | grep /media/ | grep sd | awk -F/media '{print $2}'
# lsblk -io KNAME,MOUNTPOINT | grep /media/ | grep mmcblk1 | awk -F/media '{print $2}'
path=$(lsblk -io KNAME,MOUNTPOINT | grep /media/ | grep $grepInfo | awk -F/media '{print $2}')
time=$(date +%Y_%m_%d_%H_%M_%S)

# 判断获取的路径是否为空
if [[ -n "${path}" ]]; then

    for item in ${path[@]}; do
        testFile="/media$item/FactoryTest_$time.txt"
        echo "test file name $testFile"
        # 往外部存储写入数据并读取，判断读取的数据是否和写入的数据一致
        echo $writeInfo >$testFile
        value=$(cat $testFile)
        if [[ "$writeInfo" == "${value}" ]]; then
            result=true
        else
            result=false
        fi
        # 测试完成删除测试文件
        rm $testFile
    done
fi

if $result; then
    echo "$resultInfo=[Ok]"
else
    echo "$resultInfo=[NG]"
fi
