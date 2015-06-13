import os
from PIL import Image
import datetime as dt

now=dt.datetime.now()
ago=now-dt.timedelta(minutes=30)
folder_day = dt.date.today()

resize_to = 128, 128

script_path = os.path.dirname(os.path.realpath(__file__))
log_file = open(script_path+os.sep+"askbypoll_crone.log","a")

#print(script_path,now,ago,now>ago,script_path+os.sep+'media'+os.sep+'choices'+os.sep+str(folder_day))

for root,dirs,files in os.walk(script_path+os.sep+'media'+os.sep+'choices'+os.sep+str(folder_day)):  
    for fname in files:
        path=os.path.join(root,fname)
        st=os.stat(path)    
        #mtime=dt.datetime.fromtimestamp(st.st_mtime)
        #print(mtime,ago)
        #if mtime>ago:
        #print('%s modified %s'%(path,mtime))
        #imfile, ext = os.path.splitext(path)
        #print(imfile,ext,path)
        im = Image.open(path)
        msg = "\nSize of "+path+" is "+str(im.size)+" @ "+str(dt.datetime.now())
        log_file.write(msg)
        #print(msg)
        if im.size[0] > 128 or im.size[1] > 128:
            msg = "\nResizing "+path+" @ "+str(dt.datetime.now())
            #print(msg)
            log_file.write(msg)
            im.thumbnail(resize_to)
            im.save(path)
for root,dirs,files in os.walk(script_path+os.sep+'media'+os.sep+'profile'+os.sep+str(folder_day)):  
    for fname in files:
        path=os.path.join(root,fname)
        st=os.stat(path)    
        #mtime=dt.datetime.fromtimestamp(st.st_mtime)
        #print(mtime,ago)
        #if mtime>ago:
        #print('%s modified %s'%(path,mtime))
        #imfile, ext = os.path.splitext(path)
        #print(imfile,ext,path)
        im = Image.open(path)
        msg = "\nSize of "+path+" is "+str(im.size)+" @ "+str(dt.datetime.now())
        log_file.write(msg)
        #print(msg)
        if im.size[0] > 128 or im.size[1] > 128:
            msg = "\nResizing "+path+" @ "+str(dt.datetime.now())
            #print(msg)
            log_file.write(msg)
            im.thumbnail(resize_to)
            im.save(path)
"""
for root,dirs,files in os.walk(script_path+os.sep+'media'):  
    for fname in files:
        path=os.path.join(root,fname)
        st=os.stat(path)    
        #mtime=dt.datetime.fromtimestamp(st.st_mtime)
        #print(mtime,ago)
        #if mtime>ago:
        #print('%s modified %s'%(path,mtime))
        #imfile, ext = os.path.splitext(path)
        #print(imfile,ext,path)
        im = Image.open(path)
        msg = "\nSize of "+path+" is "+str(im.size)+" @ "+str(dt.datetime.now())
        log_file.write(msg)
        #print(msg)
        if im.size[0] > 128 or im.size[1] > 128:
            msg = "\nResizing "+path+" @ "+str(dt.datetime.now())
            #print(msg)
            log_file.write(msg)
            im.thumbnail(resize_to)
            im.save(path)
"""

log_file.close()
