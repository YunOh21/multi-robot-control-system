from utils.custom_logger import Logger
from tools.task_planning import TaskPlanning

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import String
from interfaces_pkg.msg import Task, TaskRequest, RobotStatusList


log = Logger(__name__)
task_planner = TaskPlanning()

class TaskSubscriber(Node):

    def __init__(self):
        log.info("TaskSubscriber started.")
        self.received_task = None
        
        super().__init__('task_subscriber')
        self.subscription = self.create_subscription(
            TaskRequest,
            'task_request',
            self.callback,
            10)

    def callback(self, msg):
        log.info('------TaskSubscriber callback-------')
        
        # (2-1) 대기중인 로봇 확인, DB에서 로봇/업무 상태 업데이트
        # 리턴값: 수행할 로봇, 로봇에 배정된 업무, 아직 배정되지 않은 업무목록
        task_planner.robot, task_planner.item, task_planner.q = task_planner.main(msg)
        log.info((task_planner.robot, task_planner.item, task_planner.q))
        
        
class SendRobotStatusPublisher(Node):
    
    def __init__(self):
        super().__init__('send_robot_status_publisher')
        self.publisher = self.create_publisher(RobotStatusList, '/send_robot_status', 10)
        
        msg = RobotStatusList()
        
        log.info(task_planner.robot_status_list)
        
        msg.robot1.id = task_planner.robot_status_list[0][0]
        msg.robot1.status = task_planner.robot_status_list[0][1]
        msg.robot1.task = task_planner.robot_status_list[0][2]
        msg.robot1.goal = task_planner.robot_status_list[0][3]
        
        msg.robot2.id = task_planner.robot_status_list[1][0]
        msg.robot2.status = task_planner.robot_status_list[1][1]
        msg.robot2.task = task_planner.robot_status_list[1][2]
        msg.robot2.goal = task_planner.robot_status_list[1][3]
        
        msg.robot3.id = task_planner.robot_status_list[2][0]
        msg.robot3.status = task_planner.robot_status_list[2][1]
        msg.robot3.task = task_planner.robot_status_list[2][2]
        msg.robot3.goal = task_planner.robot_status_list[2][3]
        
        self.publisher.publish(msg)
        
        
class SendTaskPublisher(Node):
    def __init__(self, robot, item):
        log.info("SendTaskPublisher started.")
        
        super().__init__('send_task_publisher')
        self.publisher = self.create_publisher(Task, '/send_task_' + str(robot), 10)
        
        msg = Task()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 하나의 지점에 하나의 태스크가 있다고 가정(to do: 리스트 전송)
        x = item.waypoints.split("],")[0].split(",")[0].replace("[[", "").replace(" [", "")
        log.info(x)
        
        y = item.waypoints.split("],")[0].split(",")[1].replace(" ", "")
        log.info(y)
        
        z = item.waypoints.split("],")[0].split(",")[2].replace(" ", "").replace("]]", "")
        log.info(z)
        
        msg.position.x = float(x)
        msg.position.y = float(y)
        msg.position.z = float(z)
        
        self.publisher.publish(msg)
        
        
class SendQueuePublisher(Node):
    def __init__(self, q):
        log.info("SendQueuePublisher started.")
        
        super().__init__('send_queue_publisher')
        self.publisher = self.create_publisher(String, '/send_queue', 10)
        msg = String()
        msg.data = str(q.queue)
        self.publisher.publish(msg)
        
        
class DoneTaskSubscriber1(Node):

    def __init__(self):
        log.info("DoneTaskSubscriber1 started.")
        
        super().__init__('done_task_subscriber_1')
        self.subscription = self.create_subscription(
            String,
            'robot1/done_task',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        log.info("listening..." + msg.data)
        
        if msg.data == 'OK':
            task_planner = TaskPlanning()
            task_planner.get_done(1)
            
            
class DoneTaskSubscriber2(Node):

    def __init__(self):
        log.info("DoneTaskSubscriber2 started.")
        
        super().__init__('done_task_subscriber_2')
        self.subscription = self.create_subscription(
            String,
            'robot2/done_task',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        log.info("listening..." + msg.data)
        
        if msg.data == 'OK':
            task_planner = TaskPlanning()
            task_planner.get_done(2)


def main():
    rclpy.init()
    executor = MultiThreadedExecutor()
    
    # (1) GUI에서 요청업무 수신 -- callback으로 Task Planning과 Send Queue Publisher 실행
    task_subscriber = TaskSubscriber()
    executor.add_node(task_subscriber)
    
    # (2-2) UI에서 보낸 값이 없어도 DB에 있는 값을 찾아서 실행
    # DB에 값이 없다면 None값을 리턴받게 됨
    task_planner.robot, task_planner.item, task_planner.q, task_planner.robot_status_list = task_planner.main()
    
    log.info('----------------main-------------')
    log.info((task_planner.robot, task_planner.item, task_planner.q))
        
    # (3-1) 큐가 있다면, GUI에 토픽으로 업무 큐 전송
    if task_planner.q != None:
        send_q_publisher = SendQueuePublisher(task_planner.q)
        executor.add_node(send_q_publisher)
        
    # (3-2) 현재 로봇의 상태를 토픽으로 전송
    send_robot_status_publisher = SendRobotStatusPublisher()
    executor.add_node(send_robot_status_publisher)

    # (3) Path Planning
        
    # (4) 로봇에게 토픽으로 좌표들 전송 -- Path Planning 커스텀 안 쓸 경우 nav2가 robot_pkg에서 돌아가게 함
    # task_publisher = SendTaskPublisher(task_planner.robot, task_planner.item)
    # executor.add_node(task_publisher)
        
    # (6) 로봇에서 완료업무 수신(토픽 remap -> task_id)
    # done_task_1 = DoneTaskSubscriber1()
    # executor.add_node(done_task_1)
    
    executor.spin()
    

if __name__ == '__main__':
    main()