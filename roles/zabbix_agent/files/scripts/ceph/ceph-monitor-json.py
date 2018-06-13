#!/usr/bin/python

import sys
import os

import socket
import threading
import time
import datetime
import signal
import pwd


import commands

import json


import rados

from ceph_argparse import \
	concise_sig, descsort, parse_json_funcsigs, \
	matchnum, validate_command, find_cmd_target, \
	send_command, json_command, run_in_thread

ceph_agent_log_path="/var/log/ceph-agent.log"
socket_path = "/tmp/ceph-monitor-agent-socket"

cluster_log_list = []
rbd_du_out = ""
rbd_du_out_ofs = 0
rbd_du_out_step = 4096
warn = 0



def quit(signum, frame):
    print 'You choose to stop me.'
    sys.exit()

def find_warn(str=''):
	global warn
	if ( str.find("WARN") >= 0 ):
		warn = 1
	elif ( str.find("ERR") >= 0 ):
		warn = 2
	elif ( str.find("down") >= 0 ):
		warn = 3
	elif ( str.find("DOWN") >= 0 ):
		warn = 3
	elif ( str.find("HEALTH_OK") >= 0):
		warn = 0

def send_cmd(cluster, target=('mon', ''), cmd=None, inbuf=b'', timeout=0, verbose=False):
	try:
		ret, outbuf, outs = send_command(cluster, target, cmd, inbuf, timeout, verbose)
	except Exception as e:
		print e
	return ret, outbuf, outs


def send_socket_data(connect,data=b''):
	try:
		#print data
		connect.send(data)
	except Exception, exc:
		print exc

def main(argv):
	global warn


	os.system("touch "+ceph_agent_log_path);
	uid = pwd.getpwnam(argv[1])
	os.chown(ceph_agent_log_path, uid.pw_uid, uid.pw_gid)


	mutex = threading.Lock()

        try:
                cluster = rados.Rados(conffile='')
        except TypeError as e:
                print 'Argument validation error: ', e
                raise e

        print "Created cluster handle."

        try:
                cluster.connect()
        except Exception as e:
                print "connection error: ", e
                raise e
        finally:
                print "Connected to the cluster."






        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
                os.remove( socket_path )

        except :
		pass

        #s.bind( socket_path )
	try:
        	s.bind( socket_path )
	except :
		#os._exit(0)
		pass


	#uid = pwd.getpwnam("zabbix")
	uid = pwd.getpwnam(argv[1])
	os.chown(socket_path, uid.pw_uid, uid.pw_gid)



        s.listen(1)

	def ceph_rbd_du():
		global rbd_du_out,rbd_du_out_ofs

		while 1:
			starttime = datetime.datetime.now()
                	outbuf = ""
			target = ('mon', '')
			timeout=0
			verbose=False
			inbuf=''
			cmddict = {}
			cmddict.update({'prefix': u'osd lspools', 'format': 'json'})
			ret, outbuf, outs = send_command(cluster, target, [json.dumps(cmddict)],inbuf, timeout, verbose)
			lspools = json.loads(outbuf)
			poollist = []
			for item in lspools:
				d = {}
				#print item["poolname"]
				cmdstr = "rbd -p "+ item["poolname"] + " du"
				#print cmdstr
				images = []
				status, outbuf = commands.getstatusoutput(cmdstr)
				outarray = outbuf.split('\n')

				del outarray[0]
				if ( len(outarray) < 1 ):
					continue
				del outarray[len(outarray)-1]
				for index,value in enumerate(outarray):
					a = value.split(' ')
					tmparray = []
					for index,tmpstr in enumerate(a):
						if ( len(tmpstr) >= 1 ):
							tmparray.append(tmpstr)
					image = {}
					image["used"] = tmparray[2]
					image["provisioned"] = tmparray[1]
					image["name"] = tmparray[0]
					images.append(image)

				d["images"] = images
				d["poolname"] = item["poolname"]
				poollist.append(d)
			mutex.acquire()
			rbd_du_out_ofs=0
			rbd_du_out = "begin"+json.dumps(poollist)+"end"
			mutex.release()
			#print rbd_du_out
			while( rbd_du_out_ofs < len(rbd_du_out) ):
				time.sleep(1)
			endtime = datetime.datetime.now()
			#print (endtime - starttime).seconds
			if ( (endtime - starttime).seconds < 3600 ):
				time.sleep( 3600 - (endtime - starttime).seconds )

	t = threading.Thread(target=ceph_rbd_du)
    	t.setDaemon(True)
	t.start()


	def watch_cb(arg, line, who, stamp_sec, stamp_nsec, seq, level, msg):
		#print(line)
		#sys.stdout.flush()
		find_warn(line)
		mutex.acquire()
		cluster_log_list.insert(0,line)
		mutex.release()


	# this instance keeps the watch connection alive, but is
	# otherwise unused
	level = "info"
	run_in_thread(cluster.monitor_log, level, watch_cb, 0)

        warn = "0"
        while 1:

                conn, addr = s.accept()

                cmd = conn.recv(1024)

                if not cmd: break

                print cmd

                outbuf = ""
		target = ('mon', '')
		timeout=0
		verbose=False
		inbuf=''
		cmddict = {}

                if ( cmd == "rbd_du" ):
			global rbd_du_out,rbd_du_out_ofs,rbd_du_out_step
			#print rbd_du_out
			mutex.acquire()
			try:
				if ( len(rbd_du_out) < 1 ):
					send_socket_data(conn,"")
				else:
					#print rbd_du_out
					#print rbd_du_out_ofs
					send_socket_data(conn,rbd_du_out[rbd_du_out_ofs:rbd_du_out_ofs+rbd_du_out_step])
					rbd_du_out_ofs = rbd_du_out_ofs + rbd_du_out_step

			except Exception, exc:
                        	print exc
			mutex.release()

                	conn.close()
			continue

                elif ( cmd == "log" ):
			outbuf = ''

			mutex.acquire()
			for log_str in cluster_log_list:
				outbuf += log_str + "\n"
			del cluster_log_list[:]
			mutex.release()
			try:
				send_socket_data(conn,outbuf)
                		conn.close()
			except Exception, exc:
                        	print exc
			continue

                elif ( cmd == "warn" ):
			send_socket_data(conn,str(warn))
                	conn.close()
			continue


                elif ( cmd == "status" ):
			cmddict.update({'prefix': u'status', 'format': 'json'})
                elif( cmd == "osd_pool_stats" ):
			cmddict.update({'prefix': u'osd pool stats', 'format': 'json'})
                elif ( cmd == "osd_tree" ):
			cmddict.update({'prefix': u'osd tree', 'format': 'json'})
                elif ( cmd == "osd_df" ):
			cmddict.update({'prefix': u'osd df', 'format': 'json'})
                elif (cmd == "pg_stat" ):
			cmddict.update({'prefix': u'pg stat', 'format': 'json'})
                elif (cmd == "osd_perf" ):
			cmddict.update({'prefix': u'osd perf', 'format': 'json'})
                elif (cmd == "df" ):
			cmddict.update({'prefix': u'df', 'format': 'json'})


		ret, outbuf, outs = send_cmd(cluster, target, [json.dumps(cmddict)],inbuf, timeout, verbose)
		find_warn(outbuf)
		try:
			send_socket_data(conn,outbuf)
                	conn.close()

		except Exception, exc:
        		print exc












if __name__ == '__main__':
	try:
        	#signal.signal(signal.SIGINT, quit)
        	#signal.signal(signal.SIGTERM, quit)
        	main(sys.argv)
	except Exception, exc:
        	print exc

