# 1조 병원왔서영
## 프로젝트 목적
병원에서 의료진의 수고를 덜어주는 다중 자율 주행 로봇

## 소프트웨어 구성도
![Screenshot from 2024-01-02 10-48-45](https://github.com/addinedu-ros-3rd/ros-repo-1/assets/104709955/ac31cd37-73e2-4c35-841a-7fdff70312d0)

## Robot State Diagram
![Robot_state_diagram drawio](https://github.com/addinedu-ros-3rd/ros-repo-1/assets/104709955/52f0cc3d-c6e4-4707-9b2a-f21612535576)

## Use Case Diagram
![Use_case_diagram drawio](https://github.com/addinedu-ros-3rd/ros-repo-1/assets/104709955/f9e71c48-901e-4be6-8309-7f8c94f56d9a)

### 업무 부여 프로세스

- Task 우선순위
1) 의료진 배송요청 - 도착 후 10초 대기
2) 길안내 - 도착 후 10초 대기
3) 식사 서빙 - 도착 후 30초 대기
4) 복귀

- 추가 고려사항

1) 해당 태스크를 수행하기에 더 적합한 로봇이 있는지
    - 놀고 있음 / 놀고 있지 않지만 곧(30초 이내로) 끝남
    - 더 가까움
2) 더 멀리 있지만 놀고 있는 로봇 vs 더 가까이 있고 일을 하고 있는 로봇
    - 의료진 배송요청 : 가장 가까이 있는 로봇이 (의료진 배송요청을 이미 수행중이 아닐 때) 수행
    - 길안내 / 식사 서빙: 놀고 있는 로봇 우선
3) 모든 로봇이 일을 하고 있다면?
    - 수행을 마친 위치가 가까운 로봇에게, 우선순위가 높은 일부터 큐에 쌓음
    - 길안내 / 식사 서빙도 태스크 대기 시간이 5분은 넘어가지 않아야 함

태스크는 우선순위 큐로 관리

- pseudo code
```
if 예정 시각 5분 이내의 태스크:
  예정 태스크 할당
elif 5분 지난 태스크 있을 경우:
  5분 지난 거 할당
else:
  일반 우선순위 큐
```
