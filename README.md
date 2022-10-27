# twincar-damage-compare

## 차량 파손 전, 후 비교를 위한 서비스
- 스크립트 별 용도 설명

```
/app/common : 서비스 사용에 필요한 Function 모음
/app/config : 서비스 호출 시 사용되는 config
/app/mod_service
    controller.py : rest api 기능을 정의해 놓은 파일
    services.py : 실제 비교 서비스 기능 Function 파일

test_run.py : 로컬 테스트 용 app 구동 파일
    example) $ python test_run.py

test_client.py : 로컬 테스트 용 서비스 구동 파일
    example) $ python test_client.py
```