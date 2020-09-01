#!/usr/bin/python2.7

from urlparse import urlparse
import pdfkit
import json
import requests
import sys
import base64
import os

API_KEY = sys.argv[1]
GrafanaAddress = sys.argv[2]
ReportName = sys.argv[3]


o = urlparse(GrafanaAddress)
GrafanaAddress = o.scheme + "://" + o.netloc

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + API_KEY,
}
params = (
    ('query/', '/'),
    ('', ''),
    ('type', 'dash-db'),
)
html = ''
html+= '<!DOCTYPE html>'
html+= '<html lang="en">'
html+= '<head>'
html+= '<title>ServiceMonit - GrafanaReport</title>'
html+= '<meta charset="UTF-8">'
html+= '<meta name="viewport" content="width=device-width, initial-scale=1">'
html+= '<style>'
html+= '.header {'
html+= '  padding: 30px;'
html+= '  text-align: center;'
html+= '  background: orange;'
html+= '  color: white;'
html+= '  font-size: 30px;'
html+= '}  '
html+= '.row {'
html+= ' padding: 20px;'
html+= ' color: white'
html+= ' text-align: center;'
html+= ' background: black;'
html+= '}'
html+= '.fakeimg {'
html+= '  background-color: black;'
html+= '  padding: 20px;'
html+= '  position: center; '
html+= '}'
html+= '/* Footer */'
html+= '.footer {'
html+= '  padding: 20px;'
html+= '  text-align: center;'
html+= '  background: orange;'
html+= '  color: white; '
html+= '}'
html+= '.navbar {'
html+= '  overflow: hidden;'
html+= '  background-color: gray;'
html+= '  color: white; '
html+= '  text-align: center; '
html+= '  position: sticky;'
html+= '  position: -webkit-sticky;'
html+= '  top: 0;'
html+= '}'
html+= '.footer a.active {'
html+= '  background-color: orange;'
html+= '  color: white;'
html+= '}'
html+= '</style>'
html+= '</head>'
html+= '<body>'
html+= '<div class="header">'
html+= '  <h2>ServiceMonit</h2>'
html+= '  <p>A <b>Grafana</b>Report for you</p>'
html+= '</div>'

#print GrafanaAddress
#print API_KEY

DashboardGet = requests.get(GrafanaAddress + '/api/search/', headers=headers, params=params)
print json.dumps(DashboardGet.json(), indent=4, sort_keys=True) 

for q in DashboardGet.json():
	DashName = q[u'title']
	DashID = q[u'uid']
	html+= '<div class="navbar">'
	html+= '<h3>%s</h3>' % (q[u'title'])
	html+= '</div>'
#	print json.dumps(q, indent=4)
	DetailDashboard = requests.get(GrafanaAddress + '/api/dashboards/uid/' + str(q[u'uid']), headers=headers )
	if 'panels'  in DetailDashboard.json()[u'dashboard']:
		for w in DetailDashboard.json()[u'dashboard']['panels']:
			Height = w[u'gridPos']['h'] * 30
			Width =  w[u'gridPos']['w'] * 30
			GraphName = w[u'title']
			GraphID = w[u'id']
			GraphType = w[u'type']
		#	print json.dumps(w, indent=4)
			if w['type']  == 'row':
				html+= '<div class="row">'
				html+= '<h2>%s </h2>' % (w[u'title'])
				html+= '</div>'
			else:
				html+= '<div class="navbar">'
				html+= "<h3>Panel: %s </h3>" % (w[u'title'])
				html+= '</div>'
				URLPics = GrafanaAddress + "/render/d-solo/" + str(DashID) + "/_?from=now-1h&to=now&height=" + str(Height) + "&panelId=" + str(GraphID) + "&theme=light&width=" + str(Width) + "&timeout=600"
				print URLPics
                                GraphNameReport = ReportName + "_" + str(DashID) + "_" + str(GraphID) + ".png"

                                ImgFile = requests.get(URLPics, headers=headers)
                                open('templates/Reports/img/' + GraphNameReport, 'wb').write(ImgFile.content)
                                pngFile = open('templates/Reports/img/' + GraphNameReport,'rb')
                                base64data = pngFile.read().encode("base64").replace('\n','')
				html+= '<center><div class="fakeimg" style="height:%spx; width:%spx;">' % (Height,Width)
				html+= '<img src="data:image/png;base64,%s"/></center>' % (base64data)
                                html+= '<pre><br>'
				html+= '</div>'
                                #os.remove('templates/Reports/img/' + GraphNameReport)

html+= '<div class="footer">'
html+= '<h2>ServiceMonit</h2>'
html+= '<h3><a href="www.servicemonit.com.br" class="active">www.servicemonit.com.br</a></h3>'
html+= '</div>'
html+= '</body>'
html+= '</html>'
html_file = open("templates/Reports/" + str(ReportName) + ".html","w")
html_file.write(html.encode('utf-8'))
html_file.close()
# PDF
pdfkit.from_file("templates/Reports/" + str(ReportName) + ".html", "templates/Reports/" + str(ReportName) + ".pdf")





