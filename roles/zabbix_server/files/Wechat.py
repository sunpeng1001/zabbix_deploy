#!/usr/bin/python
#_*_coding:utf-8 _*_
import urllib,urllib2
import json
import sys
#import simplejson

reload(sys)
sys.setdefaultencoding('utf-8')

def gettoken(Corpid,Corpsecret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + Corpid + '&corpsecret=' + Corpsecret
    print  gettoken_url
    try:
        token_file = urllib2.urlopen(gettoken_url)
    except urllib2.HTTPError as e:
        print e.code
        print e.read().decode("utf8")
        sys.exit()
    token_data = token_file.read().decode('utf-8')
    token_json = json.loads(token_data)
    token_json.keys()
    token = token_json['access_token']
    return token

#def senddata(access_token,user,Tagid,Agentid,subject,content):
def senddata(access_token,Tagid,Agentid,subject,content):
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    send_values = {
        "toparty":Tagid,    #æµ¼í¢˜í°¿??èœ‚è…‘?í¢›í°¿í¢ší°¿??d?
        "msgtype":"text", #å¨‘í¢Ÿí°¿í¢˜í°€ç»«è¯²í¢µí³¢?
        "agentid":Agentid,    #æµ¼í¢˜í°¿??èœ‚è…‘?í¢›í°¿???d?
        "text":{
            "content":subject + '\n' + content
           },
        "safe":"0"
        }
    send_data = json.dumps(send_values, ensure_ascii=False)
    #send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
    send_request = urllib2.Request(send_url, send_data)
    send_request.add_header("verify","False")
    response = json.loads(urllib2.urlopen(send_request).read())
if __name__ == '__main__':
    #user = "?ã„¦í¢Ÿí°¿?í¢¤í°¢ # ??äº’æ¶“í¢¤í°¿í¢«í°¿æ·‡?í¢«í°¿,?í¢Ÿí°¿?ç¼í¢›í°¿í¢í³œ?í¢§í°¿é‡œ?èœ‚??í¢›í°¿æ±‰?í¢¨í°¿Â€í¢˜í°¿í¢®í°¿?í¢¤í°¿í¢³í³ ??20170906)
    Corpid =  'wwc0d58039247643b3'                              #CorpID???æ¶“í¢±í°¿í¢¦í°¿?í¢›í°¿í¢·í³ç’‡
    Corpsecret = 'BLr50k1d-Bi1Nh2ZWT_YvspEKgyhNx-4v7apQUpdw7M'  #corpsecretSecret????í¢í°¿???Ã˜ç€µí¢í°¿í¢©í°¿
    Agentid = "1000003"                                         # æ´í¢«í°¿í¢«í°¿ID

    Tagid = str(sys.argv[1])     #zabbixæµ¼í¢·í°¿??ãƒ§í¢±í³›ç»—??æ¶“?í¢¦í³™???í¢±í°¿è¤°í¢¬í°¿í¢·í³ç»›?D
    subject = str(sys.argv[2])  #zabbixæµ¼í¢·í°¿??ãƒ§í¢±í³›ç»—??æ¶“?í¢¦í³™???í¢¡í°¿??í¢í°¿?
    content = str(sys.argv[3])  #zabbixæµ¼í¢·í°¿??ãƒ§í¢±í³›ç»—??æ¶“?í¢¦í³™???í¢¡í°¿??í¢œí°¿?

    accesstoken = gettoken(Corpid,Corpsecret)
    senddata(accesstoken,Tagid,Agentid,subject,content)
    #senddata(accesstoken,user,Tagid,Agentid,subject,content)

