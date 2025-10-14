# 마이그레이션 파일 삭제 (불필요한 파일을 제거하여 깨끗한 상태로 시작)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# SQLite 데이터베이스 파일 삭제
rm -f db.sqlite3

# 새로운 마이그레이션 파일 생성 및 적용
python manage.py makemigrations
python manage.py migrate

# 개발 서버 실행
python manage.py runserver