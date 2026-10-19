"""Optional local Qwen backend. Run Ollama with qwen2.5:3b installed. Never expose publicly without authentication."""
import json, os, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
HOST='127.0.0.1'
PORT=int(os.getenv('STUDIO_PORT','8765'))
MODEL=os.getenv('STUDIO_MODEL','qwen2.5:3b')
OLLAMA=os.getenv('OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  if self.path!='/api/generate':
   self.send_error(404);return
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<1 or n>16000: raise ValueError('Invalid request size')
   prompt=json.loads(self.rfile.read(n))['prompt']
   if not isinstance(prompt,str) or len(prompt)>8000: raise ValueError('Invalid prompt')
   body=json.dumps({'model':MODEL,'prompt':prompt,'stream':False}).encode()
   req=urllib.request.Request(OLLAMA+'/api/generate',data=body,headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=180) as response: answer=json.load(response)
   self.reply(200,{'text':answer.get('response','')})
  except Exception as e: self.reply(502,{'error':str(e)})
 def reply(self,status,data):
  body=json.dumps(data).encode()
  self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
 print(f'Local-only Qwen API at http://{HOST}:{PORT}')
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
