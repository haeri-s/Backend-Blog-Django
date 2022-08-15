# Backend-Blog-Django
[Backend] Django REST Framework을 활용한 블로그 백엔드


<p>
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=Python&logoColor=white" />
  <img alt="Django" src="https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=Django&logoColor=white" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat-square&logo=PostgreSQL&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img alt="Google Cloud Platform" src="https://img.shields.io/badge/-Google_Cloud_Platform-4285F4?style=flat-square&logo=google-cloud&logoColor=white" />
</p>

<br/>


## Skill Stack

- Django
- Django REST Framework: RESTful API를 만들기 위해 사용함.
- Froala Editor: 블로그 글을 다양하게 편집할 수 있도록 Froala Editor를 사용함.
- Docker: GCP의 Cloud Run(Docker Container 기반임)로 서버를 운영하기 위해 Docker를 사용함.

<br/>


## 주요 기능
<img src="https://firebasestorage.googleapis.com/v0/b/proshare-312907.appspot.com/o/Api.png?alt=media" /><br/>
- [ADMIN] 블로그 글 생성하기
<br/>


## 실행

!! 실행을 위해서는 .env 파일을 만들어야 합니다.

- .env 파일

```
# .env
ENGINE="django.db.backends.postgresql_psycopg2"
DB_NAME="" # DB 이름
DB_USER="" # DB 사용자 이름
DB_PASSWORD=""  # DB 비밀번호
DB_HOST=""  # DB 호스트 주소
DB_PORT=""  # DB 포트 번호
GS_BUCKET_NAME=""  # Google Storage Bucket 이름
SECRET_KEY="" # Django Secret Key
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend" # 이메일 전송 기능
EMAIL_USE_SSL=true # SMTP ssl 여부
EMAIL_PORT=465 # SMTP 포트
EMAIL_HOST="" # SMTP 호스트 주소
EMAIL_HOST_USER="" # SMTP 사용자 ID
EMAIL_HOST_PASSWORD= # SMTP 이메일 비밀번호
SERVER_EMAIL= # SMTP 전송 이메일
DEFAULT_FROM_EMAIL="" # SMTP 기본 이메일
```


- Develop 환경: root 폴더에서 실행

```
python src/manage.py runserver
```


- Production 환경

```
gunicorn apiserver.wsgi:application -b :<<PORT Number>> --workers=<<Worker 수>> --threads <<쓰레드 수>> --reload --env ENV="prod" --preload
```

<br/>

## GCP 배포
```
# 1. GCP 에 컨테이너 빌드
gcloud builds submit --tag << GCP Container Registry 주소 >> 

# 2. GCP Cloud Run 새로운 이미지로 수정
gcloud run deploy --image << GCP Container Registry 주소 >> --platform managed
```
<br/>
