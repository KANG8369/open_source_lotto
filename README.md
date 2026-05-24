# 6/45 Lotto Web Site

대학교 Open Source 기초 과제용 Django + Docker 프로젝트입니다. 일반 사용자는 6/45 로또 번호를 수동 또는 자동으로 구매하고 당첨 여부를 확인할 수 있으며, 관리자는 판매 내역 조회, 추첨, 당첨 내역 조회를 수행할 수 있습니다.

GitHub 제출 저장소: https://github.com/KANG8369/open_source_lotto.git

## 1. 시스템 설계

### 전체 구조

```text
Browser
  |
  | HTTP
  v
web container
  - Django
  - Gunicorn
  - lotto app
  |
  | PostgreSQL protocol
  v
db container
  - PostgreSQL 16
```

### Docker multi-container 구성

`docker-compose.yml`은 두 개의 서비스를 정의합니다.

| 서비스 | 역할 |
| --- | --- |
| `web` | Django 애플리케이션 실행, migration 수행, 정적 파일 수집, Gunicorn으로 HTTP 요청 처리 |
| `db` | PostgreSQL 데이터베이스, 복권 구매/추첨/당첨 결과 데이터 저장 |

`db` 서비스에는 `postgres_data` volume을 연결하여 컨테이너가 재시작되어도 데이터가 유지되도록 했습니다.

### Django 앱 구조

| 파일 | 역할 |
| --- | --- |
| `lotto/models.py` | `Ticket`, `Draw`, `TicketResult` 모델 정의 |
| `lotto/forms.py` | 복권 구매, 복권 확인, 추첨 입력 폼 |
| `lotto/views.py` | 일반 사용자 화면과 관리자 화면 처리 |
| `lotto/urls.py` | URL과 view 연결 |
| `templates/lotto/` | 사용자/관리자 HTML 화면 |
| `lotto/tests.py` | 번호 생성, 추첨 결과, 권한, 구매 기능 테스트 |

### 데이터 모델

| 모델 | 주요 필드 | 설명 |
| --- | --- | --- |
| `Ticket` | `ticket_code`, `buyer_name`, `purchase_type`, `numbers` | 사용자가 구매한 복권 |
| `Draw` | `round_number`, `winning_numbers`, `bonus_number` | 회차별 추첨 결과 |
| `TicketResult` | `ticket`, `draw`, `rank`, `match_count`, `bonus_matched` | 복권별 당첨 확인 결과 |

### 당첨 판정 규칙

| 조건 | 결과 |
| --- | --- |
| 6개 일치 | 1등 |
| 5개 일치 + 보너스 일치 | 2등 |
| 5개 일치 | 3등 |
| 4개 일치 | 4등 |
| 3개 일치 | 5등 |
| 그 외 | 낙첨 |

## 2. 구현 과정

1. Django 프로젝트 `config`와 앱 `lotto`를 생성했습니다.
2. 강의자료의 Django MVT 구조에 맞춰 model, view, template, URLconf를 분리했습니다.
3. 일반 사용자 기능을 구현했습니다.
   - 수동 번호 구매
   - 자동 번호 구매
   - 복권 번호로 당첨 확인
4. 관리자 기능을 구현했습니다.
   - 판매 내역 확인
   - 추첨 결과 등록
   - 추첨 시 전체 복권의 당첨 결과 자동 생성
   - 회차별 당첨 내역 확인
5. Dockerfile과 Compose 파일을 작성하여 `web`, `db` multi-container 환경을 구성했습니다.
6. README에 시스템 설계, 구현 과정, 테스트 결과, AI 사용 내역을 기록했습니다.

## 3. 실행 방법

Docker Desktop이 실행 중인 상태에서 다음 명령을 실행합니다.

```bash
docker compose up --build
```

웹 브라우저에서 접속합니다.

```text
http://localhost:8000/
```

관리자 계정은 별도 터미널에서 다음 명령으로 생성합니다.

```bash
docker compose exec web python manage.py createsuperuser
```

관리자 기능은 다음 주소에서 접근합니다.

```text
http://localhost:8000/staff/
```

Django 기본 관리자 페이지는 다음 주소입니다.

```text
http://localhost:8000/admin/
```

## 4. 테스트 방법 및 결과

테스트 실행 명령:

```bash
docker compose run --rm web python manage.py test
```

테스트 항목:

| 테스트 | 기대 결과 |
| --- | --- |
| 자동 구매 | 1부터 45 사이의 중복 없는 번호 6개 생성 |
| 수동 구매 검증 | 중복 번호 입력 시 form validation 실패 |
| 추첨 결과 생성 | 당첨 번호와 복권 번호를 비교하여 등수 생성 |
| 일반 구매 view | 구매 후 복권 상세 페이지로 이동 |
| 관리자 권한 | 비로그인 사용자는 추첨 페이지 접근 불가 |
| 관리자 추첨 | staff 사용자가 추첨하면 당첨 결과 생성 |

현재 구현 기준 테스트 파일은 `lotto/tests.py`에 작성되어 있습니다.

### 검증 결과

| 명령 또는 확인 | 결과 |
| --- | --- |
| `python manage.py check` | `System check identified no issues` |
| `python manage.py test` | 6개 테스트 실행, `OK` |
| `docker compose config` | `web`, `db`, volume, healthcheck 구문 정상 |
| `docker compose up --build -d` | `lotto-web`, `lotto-db` 컨테이너 실행 성공 |
| `docker compose ps` | `lotto-db` healthy, `lotto-web` 8000 포트 매핑 확인 |
| `http://localhost:8000/` 요청 | HTTP 200 응답 확인 |
| `docker compose exec web python manage.py test` | 컨테이너 내부 6개 테스트 실행, `OK` |

## 5. GitHub 업로드 방법

아직 remote가 없다면 다음 명령으로 과제 저장소를 연결합니다.

```bash
git remote add origin https://github.com/KANG8369/open_source_lotto.git
git branch -M main
git add .
git commit -m "Implement Django Docker lotto assignment"
git push -u origin main
```

## 6. AI 도구 사용 내역

본 프로젝트는 AI 도구 Codex를 사용하여 과제 요구사항을 분석하고 초기 구현을 작성했습니다.

AI 사용 항목:

| 구분 | 사용 내용 |
| --- | --- |
| 요구사항 분석 | Django와 Docker 강의자료 내용을 바탕으로 과제 조건 정리 |
| 시스템 설계 | `web`, `db` multi-container 구조 설계 |
| 코드 작성 | Django model, form, view, template, test, Dockerfile, Compose 파일 작성 |
| 기능 추가 | 수동/자동 구매, 복권 번호 조회, 관리자 대시보드, 회차별 당첨 요약 |
| 문서화 | README의 설계, 구현 과정, 테스트 방법, AI 사용 내역 작성 |

직접 검토 및 수정해야 할 부분:

| 항목 | 설명 |
| --- | --- |
| GitHub 업로드 | 최종 소스 코드를 `KANG8369/open_source_lotto.git` 저장소에 push |
| 실행 캡처 | 과제 제출 시 브라우저 화면, 관리자 화면, 테스트 결과 화면 캡처 |
| 교수님 지시 형식 | 학교 LMS 제출 양식에 맞게 README 또는 보고서 내용 조정 |
