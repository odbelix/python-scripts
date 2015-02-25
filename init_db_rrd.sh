### change to the script directory
rrdtool create latency_db.rrd \
--step 300 \
DS:clients:GAUGE:300:0:100 \
RRA:AVERAGE:0.5:1:1500 \
