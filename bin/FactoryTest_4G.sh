#!/bin/bash

ret=0

function checkip() {
	time=0

	while true; do
		#get ip
		# IP=$(ifconfig ppp0 | grep "inet" | grep "\." | awk '{print $2}')
		IP=$(busybox ifconfig ppp0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
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

# IP=$(ifconfig ppp0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
IP=$(busybox ifconfig ppp0 | grep "inet addr" | awk '{print $2}' | awk -F: '{print $2}')
if [ -n "$IP" ]; then
	echo "4GTest=[OK]"
	exit 0
fi

if [ -e "/etc/ppp/peers/quectel-pppd.sh" ]; then
	# 连接到配置文件中的wifi
	timeout 10s /etc/ppp/peers/quectel-pppd.sh >/dev/null 2>&1
	checkip
	if [ $ret -eq 1 ]; then
		echo "4GTest=[OK]"
	else
		echo "4GTest=[NG]"
	fi
else
	echo "4GTest=[NG]"
fi
