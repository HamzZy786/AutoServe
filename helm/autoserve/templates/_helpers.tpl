{{/*
Expand the name of the chart.
*/}}
{{- define "autoserve.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "autoserve.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "autoserve.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "autoserve.labels" -}}
helm.sh/chart: {{ include "autoserve.chart" . }}
{{ include "autoserve.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "autoserve.selectorLabels" -}}
app.kubernetes.io/name: {{ include "autoserve.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "autoserve.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "autoserve.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "autoserve.frontend.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "autoserve.backend.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Worker labels
*/}}
{{- define "autoserve.worker.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: worker
{{- end }}

{{/*
ML Controller labels
*/}}
{{- define "autoserve.mlController.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: ml-controller
{{- end }}

{{/*
Database labels
*/}}
{{- define "autoserve.postgres.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: database
{{- end }}

{{/*
Redis labels
*/}}
{{- define "autoserve.redis.labels" -}}
{{ include "autoserve.labels" . }}
app.kubernetes.io/component: cache
{{- end }}
