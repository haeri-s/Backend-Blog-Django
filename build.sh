# migrate 필요시 - .gitignore에 migrations 파일 빼기
gcloud builds submit --config cloudmigrate.yaml  

# 기본
gcloud builds submit --tag asia.gcr.io/apiserver/prod-backend