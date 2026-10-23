FROM grafana/grafana-oss:13.0.2@sha256:5dad0df181cb644a14e13617b913b261a54f7d4fd4510721dba420929f35bea2

COPY docker-compose/local/grafana/provisioning /etc/grafana/provisioning
COPY docker-compose/local/grafana/dashboards /etc/grafana/dashboards

USER grafana
