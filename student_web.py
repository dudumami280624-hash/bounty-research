"""Offline browser UI for supervised local training; binds only to loopback."""
import html
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from student_lab import LESSONS, grade

PAGE='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>安全靶场学习入口</title>
<style>body{font:17px system-ui;max-width:720px;margin:40px auto;padding:0 20px;line-height:1.7}textarea{width:100%;height:160px}button,select{padding:10px;font-size:16px}pre{white-space:pre-wrap;background:#eee;padding:15px}</style>
<h1>安全靶场 · 学习入口</h1><p>离线教学入口；不上传个人信息。此页面是练习记录，不是可执行 EVM 靶场。</p>
<form method="post"><label>选择课程 <select name="lesson">{options}</select></label>
<p>{prompt}</p><label>写下漏洞原理、修复方法和实验结论</label><textarea name="answer" required></textarea>
<p><button type="submit">检查答案并显示反馈</button></p></form>{feedback}
<p>合约实战：在项目目录运行 <code>forge test --root student_lab --match-contract ReentrancyLessonTest -vv</code></p>
</html>'''
class Handler(BaseHTTPRequestHandler):
    def respond(self,body,status=200):
        data=body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)
    def render(self,lesson,feedback=""):
        if lesson not in LESSONS: lesson=next(iter(LESSONS))
        options="".join('<option value="%s"%s>%s</option>'%(html.escape(k), " selected" if k==lesson else "",html.escape(v["title"])) for k,v in LESSONS.items())
        return PAGE.format(options=options,prompt=html.escape(LESSONS[lesson]["prompt"]),feedback=feedback)
    def do_GET(self):
        if self.path!="/":
            return self.respond("Not found",404)
        self.respond(self.render(next(iter(LESSONS))))
    def do_POST(self):
        if self.path!="/": return self.respond("Not found",404)
        size=int(self.headers.get("Content-Length","0"))
        if size<1 or size>8192: return self.respond("Invalid submission",400)
        fields=parse_qs(self.rfile.read(size).decode("utf-8"))
        lesson=fields.get("lesson",[""])[0]
        answer=fields.get("answer",[""])[0]
        if lesson not in LESSONS or len(answer)>4000: return self.respond("Invalid lesson",400)
        result=grade(lesson,answer)
        feedback="<h2>反馈（需要人工审核）</h2><pre>"+html.escape(json.dumps(result,ensure_ascii=False,indent=2))+"</pre>"
        self.respond(self.render(lesson,feedback))
def main():
    print("Open http://127.0.0.1:8765 (local only)")
    HTTPServer(("127.0.0.1",8765),Handler).serve_forever()
if __name__=="__main__": main()
