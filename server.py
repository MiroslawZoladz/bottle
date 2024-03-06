from bottle import route, run, request, os, get, post, static_file
from os import walk
from pathlib import Path
from os import walk

def find_phys_addr(ip):
    with os.popen('arp -a') as f:
         for l in f.readlines():
            if (ip in l) and ('Interface' not in l):
                return l.split()[1]

def generate_download_buttons_html():
    f = []
    for (dirpath, dirnames, filenames) in walk("download"):
        f.extend(filenames)
        break
    
    s = str()
    for n in f: 
        s += f'<form method="get" action="/download/{n}"> <button type="submit">{n}</button> </form>'
    return s

            
def get_uploaders_html():
    f = []
    for (dirpath, dirnames, filenames) in walk("upload"):
        f.extend(filenames)
        break
    r = []
    
    html = ""
    for name_s in  [i.split('_')[0] for i in f] :
        html += f'<p>{name_s}</p>'
    return html
    

html = '''
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: Arial, sans-serif; }
</style>
</head>
<body>

<h3 style="color:green;">Server -> Student</h3>
{DownloadButtons}

<h3 style="color:blue;">Student -> Server</h3>
<p>Before upload update name in filename.</p>
<p>Do not use polish letters. Use capital letters. Surname first.</p>
<p>Example "ZoladzMiroslaw_Linker1_4c-cc-6a-64-e2-62.odt".</p>
<form action="/upload" method="post" enctype="multipart/form-data">
  <input type="file" name="upload" />
  <input type="submit" value="Upload" />
</form>
<p>Status: {status}</p>
<p>.</p>
<b>Uploaded</b>
{UPLOADED}
</body>
</html>

'''

@route('/')
def root():   
   
    buttons_html = generate_download_buttons_html()    
    html_ = html.replace("{status}","").replace("{DownloadButtons}",buttons_html)    
    return html_

@route('/download/<filename:path>')
def download(filename):
    print("!!!", filename)
    ip = request.environ.get('REMOTE_ADDR')
    ph_addr = find_phys_addr(ip) 
    return static_file(filename, root='./download', download=f"KowalskiJan_{Path(filename).stem}_{ph_addr}{Path(filename).suffix}")

@route('/upload', method='POST')
def upload():
    upload     = request.files.get('upload')
    filename = Path(upload.filename)    
    ip = request.environ.get('REMOTE_ADDR')
    client_ph_addr = find_phys_addr(ip) 
    if (filename.stem != 'empty') and ((filename.suffix == '.odt') or (filename.suffix == '.zip')) and (len(filename.stem.split('_')) == 3) :  
        file_ph_addr = filename.stem.split('_')[-1]
        if client_ph_addr==file_ph_addr:
            path = "./upload/"+str(filename)
            if os.path.exists(path):
                os.remove(path)
            upload.save("./upload")
            status = "OK"
            print("UPLOADERS", get_uploaders_html())
        else:
            status = "ERROR"
    else:
        status = "ERROR"
        
    global html     
    buttons_html = generate_download_buttons_html()    
    html_ = html.replace("{status}",status).replace("{DownloadButtons}",buttons_html).replace("{UPLOADED}",get_uploaders_html())  
    return html_


#192.168.1.11 
run(host='192.168.1.44', port=8000, debug=True,server='paste')

# or
