import os
import sys
import socket
import FloorHeater

html = """<!DOCTYPE html>
<html>
    <head>
    <meta name="viewport" content="width=device-width" />
    <title>床暖房</title>
    </head>
    <body> <h1>床暖房</h1>
        <table border="1"> <tr><th>場所</th><th>状態</th></tr> %s </table>
        <form style='display: inline' method=POST action="">
        <input type=hidden name=req value=ON>
        <input type=submit value="オン">
        </form>
        <form style='display: inline' method=POST action="">
        <input type=hidden name=req value=OFF>
        <input type=submit value="オフ">
        </form>
    </body>
</html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)


def start():
    this = sys.modules[__name__]
    html = this.html
    addr = this.addr
    s = this.s
    print('listening on', addr)

    while True:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        do_on = False
        do_off = False
        do_icon = False
        is_post = False
        post_len = "0"
        host = ""
        while True:
            line = cl_file.readline()
            if "GET" in line and "ON" in line:
                do_on = True
            if "GET" in line and "OFF" in line:
                do_off = True
            if "GET" in line and "apple-touch-icon.png" in line:
                do_icon = True
            if "POST" in line:
                is_post = True
            if is_post and "Content-Length:" in line:
                _, post_len = str(line, "").split(": ", 1)
            if "Host:" in line:
                _, host = str(line, "").split(": ", 1)
            if not line or line == b'\r\n':
                break
        if is_post:
            line = cl_file.read(int(post_len))
            if "ON" in line:
                do_on = True
            if "OFF" in line:
                do_off = True
        if do_on:
            FloorHeater.on()
        if do_off:
            FloorHeater.off()
        if is_post:
            cl.send("HTTP/1.0 302 Found\r\n")
            cl.send("Location: http://" + host + "/#\r\n")
            cl.send("\r\n")
            cl.close()
        elif do_icon:
            fn = 'apple-touch-icon.png'
            ST_SIZE = 6
            size = os.stat(fn)[ST_SIZE]
            cl.send("HTTP/1.0 200 OK\r\n")
            cl.send("Content-Type: image/png\r\n")
            cl.send("Content-Length: " + str(size) + "\r\n")
            cl.send("\r\n")
            f = open(fn, 'rb')
            while True:
                data = f.read(1024)
                if len(data) == 0:
                    break
                cl.write(data)
            f.close()
            cl.send("")
            cl.close()

        else:
            cl.send("HTTP/1.0 200 OK\r\n")
            cl.send("Content-Type: text/html; charset=utf-8\r\n")
            cl.send("\r\n")
            rows = [
                '<tr><td>一階</td><td>%s</td></tr>' %
                ("オン" if FloorHeater.p5.value() == 0 else "オフ")
            ]
            response = html % '\n'.join(rows)
            cl.send(response)
            cl.close()


start()
