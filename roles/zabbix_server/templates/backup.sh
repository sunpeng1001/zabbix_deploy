#!/usr/bin/env bash
#set -x
#:***********************************************
#:Program: Mariadb backup script
#:
#:Author: ohmyzakka@gmail.com
#:
#:History: 2017-09-07
#:
#:Version: 1.0
#:***********************************************

#Note: num=1 start backup
num=1
export PATH=/usr/local/mysql/bin:$PATH

HOST=localhost
PORT=3306
BAKUSER=root
BAKPASSWD=
BAKCNF=/etc/my.cnf
OBJECK_NAME=zabbix_object
BASEDIR={{ basedir }}
PHYSICAL_XTRA_BAKDIR=$BASEDIR/backup/xtrabackup/xtradata
PHYSICAL_XTRA_LOGDIR=$BASEDIR/backup/xtrabackup/xtralog
LOGIC_DUMP_BAKDIR=$BASEDIR/backup/mysqldump/dumpdata
LOGIC_DUMP_LOGDIR=$BASEDIR/backup/mysqldump/dumplog
CURRENTDATE=`date '+%Y%m%d'`
CURRENTTIME=`date '+%Y%m%d%H%M%S'`
FULLXTRA_BAKDIR=$PHYSICAL_XTRA_BAKDIR/$CURRENTDATE
MYSQLCMD="/usr/bin/mysql -u$BAKUSER -p$BAKPASSWD -S {{ mysql_datadir }}/mysql.sock"
MYSQLDUMPCMD="/usr/bin/mysqldump -u$BAKUSER -p$BAKPASSWD -S /var/lib/mysql/mysql.sock"
MYSQLXTRACMD="/usr/bin/innobackupex  --defaults-file=$BAKCNF --user=$BAKUSER --password=$BAKPASSWD --host=localhost --socket={{ mysql_datadir }}/mysql.sock"
DATE_RM=`date -d '2 days ago' '+%Y%m%d'`
#backup work dir
workpath()
{
if [ ! -d $PHYSICAL_XTRA_BAKDIR ]; then
	mkdir -p $PHYSICAL_XTRA_BAKDIR
fi

if [ ! -d $PHYSICAL_XTRA_LOGDIR ]; then
	mkdir -p $PHYSICAL_XTRA_LOGDIR
fi

if [ ! -d $LOGIC_DUMP_BAKDIR ]; then
	mkdir -p $LOGIC_DUMP_BAKDIR
fi

if [ ! -d $LOGIC_DUMP_LOGDIR ]; then
	mkdir -p $LOGIC_DUMP_LOGDIR
fi

if [ ! -d $CURRENTDATE ];then
        mkdir -p $LOGIC_DUMP_BAKDIR/$CURRENTDATE
fi

#if [ ! -d /var/remotebak/binlog/$CURRENTDATE ];then
#        mkdir -p /var/remotebak/binlog/$CURRENTDATE
#fi

}

#Physical: rm old file
rm_physical_oldbak()
{
	rm -rf  $PHYSICAL_XTRA_BAKDIR/$DATE_RM

}

#Physical: compress last day backup file
compress_physical_bak()
{
        LASTDT=`date -d last-day +%Y%m%d`
        cd $PHYSICAL_XTRA_BAKDIR
        tar -zcf xtrabak_$LASTDT.tar.gz $LASTDT*
     #   rm -rf $LASTDT*
}

#Logic: rm old file
rm_logic_oldbak()
{
        find $LOGIC_DUMP_BAKDIR -mtime +1 |xargs rm -rf
}

#Logic: compress last day backup file
compress_logic_dump()
{
        LASTDT=`date -d last-day +%Y%m%d`
        cd $LOGIC_DUMP_BAKDIR
        tar -zcf dumpbak_$LASTDT.tar.gz $LASTDT*
     #   rm -rf $LASTDT*
}

#Backup db function
logic_dump_fulldb()
{
	$MYSQLDUMPCMD --all-databases --single-transaction   --triggers --routines --events  > $LOGIC_DUMP_BAKDIR/$CURRENTDATE/full_db.dmp
  cp /etc/my.cnf $LOGIC_DUMP_BAKDIR/$CURRENTDATE/$OBJECK_NAME.cnf
}

logic_dump_tabledb()
{
	$MYSQLCMD -e "show databases;"|grep -vE "(Database|_schema)" > $LOGIC_DUMP_BAKDIR/db_list
	while read DBNAME
	do

	if [ ! -d $DBNAME ];then
		mkdir -p $LOGIC_DUMP_BAKDIR/$CURRENTDATE/$DBNAME
	fi

		$MYSQLCMD -e "use $DBNAME; show tables;" |grep -vE "(Tables_in|general_log|slow_log)" > $LOGIC_DUMP_BAKDIR/table_list
		#xmysql -e "flush tables with read lock;"

		while read TABLENAME
		do
			$MYSQLDUMPCMD --single-transaction --hex-blob --triggers --routines --events $DBNAME $TABLENAME  > $LOGIC_DUMP_BAKDIR/$CURRENTDATE/$DBNAME/$TABLENAME.sql

    		done < $LOGIC_DUMP_BAKDIR/table_list

	done < $LOGIC_DUMP_BAKDIR/db_list
	echo "logic full backup & Sechema backup on `date '+%Y%m%d %H:%M:%S'`" >> $LOGIC_DUMP_LOGDIR/backup_history.log
	rm -rf $LOGIC_DUMP_BAKDIR/db_list
	rm -rf $LOGIC_DUMP_BAKDIR/table_list
}

physical_xtra_fulldb()
{
        $MYSQLXTRACMD  --parallel=8 --throttle=50 --slave-info --no-timestamp  $FULLXTRA_BAKDIR  >> $PHYSICAL_XTRA_LOGDIR/xtrabak_$CURRENTTIME.log 2>&1
}

#Copy to remote server
cptoremote()
{
  echo "cp $1 to /remote"
	cp -rp $1 $2 /var/remotebak
}

#Backup action
case $num in
   1)
    echo  "Full backup on `date '+%Y%m%d %H:%M:%S'`" >> $PHYSICAL_XTRA_LOGDIR/backup_history.log
    workpath
   rm_physical_oldbak
   #rm_logic_oldbak
   physical_xtra_fulldb
   #logic_dump_fulldb
   #logic_dump_tabledb
   #compress_physical_bak
   #compress_logic_dump
	;;
   *)
   echo "error on `date '+%Y%m%d %H:%M:%S'`" >> $PHYSICAL_XTRA_LOGDIR/backup_history.log
	;;
esac
