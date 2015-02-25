#!/usr/local/bin/bash
## Graph for last 24 hours 
	
rrdtool graph latency_graph.png \
-w 785 -h 120 -a PNG \
--start -3600 --end now \
--font DEFAULT:7: \
--title "Clients for AP" \
--watermark "`date`" \
--vertical-label "Number(clients)" \
--lower-limit 0 \
--right-axis 100:0 \
DEF:clients=latency_db.rrd:clients:AVERAGE \
LINE:clients#0000FF:Clientes \
GPRINT:clients:AVERAGE:"Avg\: %5.2lf" \

 
## copy to the web directory
#cp latency_graph.png /var/www/htdocs/
