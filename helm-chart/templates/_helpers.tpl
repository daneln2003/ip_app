{{/*
Generate the name of the chart
*/}}
{{- define "ip-app.name" -}}
ip-app
{{- end }}

{{/*
Generate the full name of the resource
*/}}
{{- define "ip-app.fullname" -}}
{{ .Release.Name }}
{{- end }}
