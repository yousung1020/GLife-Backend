📑 API 명세서 (현재 코드 기준)
1. Organizations (회사 & 직원 관리)
회사

POST /api/organizations/companies/

회사 생성 (회원가입)

GET /api/organizations/companies/

회사 목록 조회

GET /api/organizations/companies/{id}/

특정 회사 상세 조회

PUT /api/organizations/companies/{id}/

회사 정보 수정

DELETE /api/organizations/companies/{id}/

회사 삭제

로그인

POST /api/organizations/login/

사업자등록번호(biz_no) + 비밀번호 로그인

JWT 토큰 발급

직원

GET /api/organizations/employees/

로그인된 회사 소속 직원 목록

POST /api/organizations/employees/

직원 생성

GET /api/organizations/employees/{id}/

직원 상세 조회

PUT /api/organizations/employees/{id}/

직원 수정

DELETE /api/organizations/employees/{id}/

직원 삭제

POST /api/organizations/employees/bulk/

직원 대량 업로드(JSON 배열)

2. Courses (교육 과정)

GET /api/courses/

교육 과정 목록 조회

POST /api/courses/

과정 생성

GET /api/courses/{id}/

특정 과정 상세 조회

PUT /api/courses/{id}/

과정 수정

DELETE /api/courses/{id}/

과정 삭제

3. Enrollments (수강 신청)

GET /api/enrollments/

수강신청 목록 조회

POST /api/enrollments/

수강신청 생성

GET /api/enrollments/{id}/

특정 수강신청 상세 조회

PUT /api/enrollments/{id}/

수강 상태 수정

DELETE /api/enrollments/{id}/

수강신청 취소

4. AI (동작 인식 & 평가)

GET /api/ai/motion-types/

동작 종류 목록 조회

POST /api/ai/motion-types/

동작 종류 등록

GET /api/ai/motion-recordings/

동작 녹화 데이터 조회

POST /api/ai/motion-recordings/

동작 녹화 데이터 업로드

POST /api/ai/evaluate/

업로드된 사용자 동작과 참조 동작 비교 (DTW 기반 평가)

POST /api/ai/devices/

Unity 장비 인증 (센서 등록)
