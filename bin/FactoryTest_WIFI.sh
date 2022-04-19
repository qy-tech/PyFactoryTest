#!/bin/bash

ret=0

function checkip() {
	time=0

	while true; do
		#get ip
		# IP=$(ifconfig wlan0 | grep "inet" | grep "\." | awk '{print $2}')
		IP=$(busybox ifconfig wlan0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
		if [ -z "$IP" ]; then
			if [[ $time -eq 15 ]]; then
				ret=0
				break
			else
				time=$(($time + 1))
				sleep 1
			fi
		else
			ret=1
			break
		fi
	done
}

if [ -z "$1" ] || [ -z "$2" ]; then
	echo "WIFITest=[NG]"
	exit 1
else
	echo "ssid $1 password $2"
fi

function getSignalLevel() {
	signalLevel=$(iwconfig wlan0 | grep -oP "(Signal level=*.?\d+\sdBm)")
	echo "Display=[$signalLevel]"
}

# IP=$(ifconfig wlan0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
IP=$(busybox ifconfig wlan0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
if [ -n "$IP" ]; then
	getSignalLevel
	echo "WIFITest=[OK]"
	exit 0
fi

wlan1=$(ifconfig | grep wlan1)
if [ -n "$wlan1" ]; then
	softapDemo stop
	ifconfig wlan0 down
	sleep 1
	ifconfig wlan0 up
	sleep 1
fi

# 设置wifi连接可用
nmcli connection up ifname wlan0
# 断开当前连接的wifi
# nmcli device disconnect wlan0
# 搜索配置文件中的wifi是否可用
psk_wifi=$(nmcli dev wifi list | grep -w $1)
if [ -n "$psk_wifi" ]; then
	# 连接到配置文件中的wifi
	nmcli dev wifi connect $1 password $2 >/dev/null 2>&1
	sleep 1
	checkip
	if [ $ret -eq 1 ]; then
		getSignalLevel
		echo "WIFITest=[OK]"
	else
		echo "WIFITest=[NG]"
	fi
else
	echo "WIFITest=[NG]"
fi
