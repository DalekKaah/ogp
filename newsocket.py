##!/usr/bin/env python2         
## newsocket.py

## uncomment above for autorun at boot------

## OGP Telescope  --  Main Module

## LIBRARIES 

import focus
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import time
import serial
import picamera
from SimpleCV import *
import os
## our library
from ogplab import *
import ircam
from chase2 import *
import ephem

## some important variables

s = serial.Serial('/dev/ttyUSB0', 9600)                     ## serial to arduino

c2 = SimpleCV.Camera(0,{ "width": 544, "height": 288 })          ## opens a camera
##c = SimpleCV.Camera(1,{ "width": 544, "height": 288 })           ## or two
js = SimpleCV.JpegStreamer('0.0.0.0:8080')                        ## opens socket for jpeg out
time.sleep(4)                                               ## strategic buffering, possibly unnecessary
c2.getImage().save(js.framebuffer)                 ## push a jpeg to the jpeg socket

cam_mode = int(3)

##autocalibration
acu = int(1)
acd = int(1)
acl = int(1)
acr = int(1)

showimage = int(1)
mapsize = int(10)
stepsize = int(100)
nudgesize =int(50)
stat = "ogp"
sqx = int(272)
sqy = int(144)
moon = ephem.Moon()
orlando = ephem.Observer()
orlando.lat = '28.41'
orlando.lon =  '-81.29'

class WSHandler(tornado.websocket.WebSocketHandler):      

    def open(self):
        print 'New connection was opened 1'
        self.write_message("telescope listening")   ## sending message through text socket
        x = int(0)
        y = int(0)
        z = int(0)
        self.x = 0
        self.y = 0
        self.z = 0
        self.mapsize = mapsize
        self.showimage = showimage
        self.stepsize = stepsize
        self.cam_mode = cam_mode
        self.sqx = sqx
        self.sqy = sqy
        s.write('n')
        time.sleep(2)
        self.write_message(s.readline())

        
        

    def on_message(self, message):

        print 'Incoming message:', message      ## output message to python
        if message.isdigit():
            digits = int(message)
            print 'digits_'+ str(digits)
            if digits>9:
                s.write('x'+ str(digits))

        msgsplit = message.split("_")
        print msgsplit[0]
        
        showimage = self.showimage
        mapsize = self.mapsize
        stepsize = self.stepsize
        x = self.x
        y = self.y
        z = self.z
        stat = "ogp"
        sqx = self.sqx
        sqy=self.sqy
        cam_mode = self.cam_mode
        wsh2=self

        if msgsplit[0] == 'moon':
            print "moon"
            
            client_utc = str(msgsplit[1] + "  " + msgsplit[2])
            d = ephem.Date(client_utc)
            orlando.date = d
            print d
            
            moon.compute(orlando)
            moonaz = str(moon.az)
            moonalt = str(moon.alt)
            ticks = str(time.time())
            self.write_message("moon_" + moonalt + "_" + moonaz )
            self.write_message("time_" + client_utc)

            moonaz2 = moonaz.split(":")
            moonalt2 = moonalt.split(":")
            print moonaz2[0]
            print moonalt2[0]

            moonalt3 = moonalt2[0]
            if moonalt3 >= 12:
                moonalt4 = "x"+ str(moonalt3)
                s.write(moonalt4)
                

##            moonaz3 = moonaz2[0]
##            if moonaz3 >= 3:
##                moonaz4 = int(moonaz3) + 100
##                s.write(moonaz4)




            
        if message == 'focus':
            focusobj = focus.focus1()
            focus2 = focusobj.fuFind()
            

            
        if message =='j':            ##    switches for incoming socket events
            print "j"
            x = x + 1
            self.x = x
            self.write_message("echo: " + message + " right " )    
            s.write('s')
            time.sleep(.5)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='c4':
            cam_mode = 4
            self.cam_mode = cam_mode
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()
            self.write_message("echo: " + message + "long exposure mode " + str(cam_mode) )
            
        if message =='c3':
            cam_mode = 3
            self.cam_mode = cam_mode
            img1 = c2.getImage()
            blobs = img1.findBlobs()
            if blobs:
                img1.drawCircle((blobs[-1].x,blobs[-1].y),30,color=(255,255,255))
                img1.drawCircle((blobs[-1].centroid()),10,color=(255,100,100))
                rgb1 = blobs[-1].meanColor()
                cent = blobs[-1].centroid()

                img1.drawText(str(stat), 10, 10, fontsize=50)
                img1.drawText(str(x), 10, 70, color=(255,255,255), fontsize=25)
                img1.drawText(str(y), 10, 100, color=(255,255,255), fontsize=25)
                img1.drawRectangle(sqx,sqy,25, 25,color=(255,255,255))

                img1.drawText(str(z), 10, 230, color=(255,255,255), fontsize=15)https://github.com/opengimbal/ogp/graphs
                img1.drawText(str(cent), 10, 250, color=(255,255,255), fontsize=15)
                img1.drawText(str(rgb1), 10, 270, color=(255,255,255), fontsize=15)
            img1.save(js.framebuffer)
            self.write_message("echo: " + message + " " + str(cam_mode) )    

        if message =='c2':
            cam_mode = 2
            self.cam_mode = cam_mode
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()
            self.write_message("echo: " + message + " " + str(cam_mode) )    

        if message =='c1':
            cam_mode = 1
            self.cam_mode = cam_mode
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()
            self.write_message("echo: " + message + " " + str(cam_mode) )    

        if message =='h':
            print "h"
            x = x - 1
            self.x = x
            self.write_message("echo: " + message + " left" )
            s.write('q')
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()
            
        if message == 'squ':
            print "squ"
            sqy = self.sqy
            sqy = sqy + 25
            self.write_message("echo: "+str(sqy)+" sighting square")
            self.sqy=sqy
        if message == 'sqd':
            print "sqd"
            sqy = self.sqy
            sqy = sqy - 25
            self.write_message("echo: "+str(sqy)+" sighting square")
            self.sqy=sqy
        if message == 'sql':
            print "sql"
            sqx = self.sqx
            sqx = sqx + 25
            self.write_message("echo: "+str(sqx)+" sighting square")
            self.sqx=sqx
        if message == 'sqr':
            print "sqr"
            sqx = self.sqx
            sqx = sqx - 25
            self.write_message("echo: "+str(sqx)+" sighting square")
            self.sqx=sqx
            
        if message =='+':
            print "+"
            stepsize = self.stepsize
            if stepsize < 1975:
                stepsize = stepsize + 25
                stepsizeb = stepsize +1000
            s.write('x'+ str(stepsizeb))
            self.write_message("echo: " + str(stepsize) + " stepsize plus" )
            self.stepsize = stepsize
        if message =='-':
            print "-"
            stepsize = self.stepsize
            if stepsize > 0. :
                stepsize = stepsize -25
                stepsizeb = stepsize +1000
            s.write('x'+str(stepsizeb))
            self.write_message("echo: " + str(stepsize) + " stepsize minus" )
            self.stepsize = stepsize

        if message =='p':
            stat = "mapsizing"
            print "p"
            mapsize = mapsize + 1
            self.mapsize= mapsize
            self.write_message("echo: " + message + " mapsize " + str(mapsize))
            print "n"
            self.write_message("echo: " + message + " map" )
            print stepsize
            m = stepsize
            wsh = tornado.websocket.WebSocketHandler        ## wsh holds some socket info
            wsh2 = self                                    ## wsh2 holds the name of the instance  
            map = so(mapsize, m, js, wsh, wsh2, c2, cam_mode)               ##  make an istance of the mapper --SO stands for seek out 
            self.map = map
            map.histo()                                   ##  histogram is necessary before run
  
        if message =='l':
            stat = "mapsizing"
            print "l"
            mapsize = mapsize - 1
            self.mapsize = mapsize
            self.write_message("echo: " + message + " mapsize " + str(mapsize))
            print "n"
            self.write_message("echo: " + message + " map" )
            print stepsize
            m = stepsize
            wsh = tornado.websocket.WebSocketHandler        ## wsh holds some socket info
            wsh2 = self                                    ## wsh2 holds the name of the instance  
            map = so(mapsize, m, js, wsh, wsh2, c2, cam_mode)               ##  make an instance of the mapper --SO stands for seek out 
            self.map = map
            map.histo()                                   ##  histogram is necessary before run
  
            
        if message =='y':
            print "y"
            y = y + 1
            self.y = y
            self.write_message("echo: " + message + " up   ")
            s.write('w')
            time.sleep(.5)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='g':
            print "g"
            y = y - 1
            self.y = y
            self.write_message("echo: " + message + " down   ")
            s.write('a')
            time.sleep(.5)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='z':
            stat = "mapping down"
            print "z- map down"
            y = y - 1
            self.y = y
            self.write_message("echo: " + message + " map down   ")
            s.write('l')
            time.sleep(1)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='a':
            stat = "mapping left"
            print "a- map left"
            x = x-1
            self.x = x
            self.write_message("echo: " + message + " map left   ")
            d = 'l'
            ms = stepsize
            s.write('k')
            time.sleep(1)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='w':
            stat = "mapping up"
            print "w- map up"
            y = y + 1
            self.y = y
            self.write_message("echo: " + message + " map up   ")
            d = 'u'
            ms = stepsize
            s.write('o')
            time.sleep(1)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='s':
            stat = "mapping right"
            print "s- map right"
            x = x + 1
            self.x = x
            self.write_message("echo: " + message + " map right   ")
            d = 'r'
            ms = stepsize
            s.write('p')
            time.sleep(1)
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()

        if message =='b':           ## MAPPER 
            print "b"
            s.write('n')
            time.sleep(1)
            self.write_message(s.readline())
            self.write_message("echo: " + message + " map" )        
            m = stepsize
            wsh = tornado.websocket.WebSocketHandler        ## wsh holds some socket info
            wsh2 = self       ## wsh2 holds the name of the instance  
            map = self.map
            map.run()                        

        if message =='n':           ## MAPPER 
            print "n"
            self.write_message("echo: " + message + " map" )
            print stepsize
            m = stepsize
            wsh = tornado.websocket.WebSocketHandler        ## wsh holds some socket info
            wsh2 = self                                    ## wsh2 holds the name of the instance  
            map = so(mapsize, m, js, wsh, wsh2, c2, cam_mode)               ##  make an istance of the mapper --SO stands for seek out 
            self.map = map
            map.histo()                                   ##  histogram is necessary before run
           ## print map.mySet                      ## print map log data array

        if message == 'c':
            wsh = tornado.websocket.WebSocketHandler        ## wsh holds some socket info
            wsh2 = self                                    ## wsh2 holds the name of the instance  
            cchase = chase3(js, wsh, wsh2, c2, sqx, sqy, cam_mode)
            cchase.run()

        if message == 'x':
            showimage = showimage - 1
            self.showimage = showimage
            pth1 = "/var/www/images/image"
            pth3 = ".png"
            pth = pth1 + str(showimage) + pth3
            apath = os.path.abspath(pth)
            self.write_message(pth)
            print showimage
            img1 = Image(pth)
            img1.save(js.framebuffer)

            
        if message == 'v':
            showimage = showimage + 1
            self.showimage = showimage
            pth1 = "/var/www/images/image"
            pth3 = ".png"
            pth = pth1 + str(showimage) + pth3
            apath = os.path.abspath(pth)
            self.write_message(pth)
            print showimage
            img1 = Image(pth)
            img1.save(js.framebuffer)
##

        if message =='t':
            print "t"
            s.write('t')
            time.sleep(1)
            s.write('c')
            self.write_message("echo: " + message + " focus out")            
        if message =='f':
            print "f"
            s.write('f')
            time.sleep(1)
            s.write('c')

            self.write_message("echo: " + message + " focus in")            


        if message =='2':
            print "2"
            s.write('2')
            self.write_message("echo: " + message + " 2")

        if message =='3':
            print "3"
            s.write('3')
            self.write_message("echo: " + message + "3")
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()


        if message =='4':
            print "4"
            s.write('4')
            self.write_message("echo: " + message + "4")
            

        if message =='7':
            print "7"
            s.write('6')
            self.write_message("echo: " + message + " 7")

        if message =='mx':
            print "sensor"
            s.write('n')
            time.sleep(1)
            self.write_message(s.readline())

        if message =='8':
            print "8"
            s.write('8')
            self.write_message("echo: " + message + " 8")
            irpic = ircam.pinoir2(js, cam_mode, c2, x, y, z, stat,sqx,sqy,s,wsh2)
            irpic.run()


        if message =='9':
            print "9"
            s.write('9')
            self.write_message("echo: " + message + " 9")


    def on_close(self):                       ##  if you lose the socket
        print 'Connection was closed...'

application = tornado.web.Application([        ##creates instance of socket
    (r'/ws', WSHandler),                 
])


if __name__ == "__main__":                       ##    since this is the main module
    http_server = tornado.httpserver.HTTPServer(application)      ## opens the socket
    http_server.listen(8888)                                     ## on this port
    tornado.ioloop.IOLoop.instance().start()        ##   this starts the threaded socket loop
        
