import time
import numpy as np

class Semaphore:
    def __init__(self,board, sensor1, sensor2):
        self.sensor1 = board.get_pin(sensor1)
        self.sensor2 = board.get_pin(sensor2)
        self.switch_state("red")
        total_active_time=10
        self.orange_time=2
        self.green_time=total_active_time-self.orange_time

    def acquire_sensor_data(self):
        sensor_data = (self.sensor1.read(),self.sensor2.read())
        return sensor_data

    def switch_state(self,state):
        self.state=state
        actions={"red":self.red,"green":self.green, "yellow":self.yellow}
        self.action = actions[self.state]

    def activity(self):
        return self.action()

    def red(self):
        return self.acquire_sensor_data()

    def green(self):
        elapsed=0
        initial_state=self.acquire_sensor_data()
        while elapsed<self.green_time:
            elapsed+=1
            time.sleep(1)
            if sum(self.acquire_sensor_data())<sum(initial_state):
                break

    def yellow(self):
        time.sleep(self.orange_time)


class EventManager:
    def __init__(self,board,*sensors):
        self.semaphores=np.array([Semaphore(board,*sensors[i]) for i in range(4)])

    def monitor(self):
        states= np.array([semaphore.acquire_sensor_data() for semaphore in self.semaphores])
        self.longer_queue_semaphores=self.semaphores[np.where(np.sum(states,axis=1)==np.max(np.sum(states,axis=1)))[0]]
        self.shorter_queue_semaphors=self.semaphores[np.where(np.sum(states,axis=1)==1)[0]]

    def act(self,priority):
        for semaphore in self.longer_queue_semaphores:
            semaphore.switch_state("green")
            if self.longer_queue_semaphores.size == 1: break
            semaphore.switch_state("yellow")
            semaphore.switch_state("red")