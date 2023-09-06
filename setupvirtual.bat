@echo off
setlocal

chcp 65001

:: 가상환경 이름
set VENV_NAME=env

echo 가상 환경을 설치 합니다. 이미 설치되어 있는 경우 불필요합니다.
set /p input=계속하려면 'y'를 입력하세요:
if '%input%' == 'Y' goto START:
if '%input%' == 'y' goto START:

goto EXIT:

:START
	:: Python 가상 환경 생성
	python -m venv %VENV_NAME%

	:: 가상 환경 활성화
	call %VENV_NAME%\Scripts\activate

	:: 필요한 패키지 설치
	python -m pip install --upgrade pip
	pip install selenium
	pip install pandas
	pip install beautifulsoup4

	:: 다른 설정이나 명령을 추가할 수 있습니다.

	:: 가상 환경 비활성화
	:: deactivate
:EXIT