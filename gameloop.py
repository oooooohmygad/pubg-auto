import os
import time
import random
import ctypes
import pyautogui
import pydirectinput
import numpy
from myopencv.myopencv import ImageFinder


#    插入随机延迟
def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))


#    模拟按键按下和释放
def press_key(key):
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    random_sleep(0.05, 0.2)  # 模拟人类的按键时长
    ctypes.windll.user32.keybd_event(key, 0, 2, 0)


# 随机化鼠标移动和点击，使用曲线移动
def move_and_click(x, y):
    # 轻微随机化目标位置，模拟误差，但不影响整体坐标
    x_offset = random.randint(-3, 3)
    y_offset = random.randint(-3, 3)

    # 生成贝塞尔曲线控制点
    start_pos = pyautogui.position()  # 获取当前鼠标位置
    end_pos = (x + x_offset, y + y_offset)  # 目标位置
    control_point = ((start_pos[0] + end_pos[0]) // 2 + random.randint(-100, 100),
                     (start_pos[1] + end_pos[1]) // 2 + random.randint(-100, 100))  # 控制点

    # 生成贝塞尔曲线路径
    def bezier_curve(t, p0, p1, p2):
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

    # 分割路径为多个点，模拟曲线
    points = []
    for i in numpy.linspace(0, 1, num=80):  # 50个点来平滑移动
        x_curve = bezier_curve(i, start_pos[0], control_point[0], end_pos[0])
        y_curve = bezier_curve(i, start_pos[1], control_point[1], end_pos[1])
        points.append((int(x_curve), int(y_curve)))

    # 根据生成的曲线路径移动鼠标
    for point in points:
        pyautogui.moveTo(point, duration=0.01)  # 逐点移动，控制每次移动的时长

    # 延迟模拟自然移动
    random_sleep(0.3, 0.8)
    pyautogui.click()

#    随机移动鼠标到无关位置，模拟人为干扰
def random_mouse_move():
    screen_width, screen_height = pyautogui.size()
    random_x = random.randint(0, screen_width)
    random_y = random.randint(0, screen_height)
    pyautogui.moveTo(random_x, random_y, duration=random.uniform(0.5, 2.0))



class GameState:
    HOME = "home"
    START = "start"
    LOADING = "loading"
    LOADING1 = "loading1"
    GAME = "game"
    BACKHOME1 = "backhome1"
    BACKHOME2 = "backhome2"
    BACKHOME3 = "backhome3"
    BACKHOME4 = "backhome4"
    BACKHOMEALL = "backhomeall"


class gameloop:
    def __init__(self):
        self.is_state = False
        self.c = None

    def gameLoop(self, timeout=5, flaytimeout=25, imgopcv=0.8, saveLog=True):
        clash = ImageFinder(imgopcv)
        images = self.getImagesMap()
        # 检查资源文件
        for key, value in images.items():
            if isinstance(value, list):
                for item in value:
                    if not os.path.exists(item):
                        print(f"资源文件不存在: {item}")
                        self._mylogs(f"资源文件不存在: {item}")
            else:
                if not os.path.exists(value):
                    print(f"资源文件不存在: {value}")
                    self._mylogs(f"资源文件不存在: {value}")
        # 禁用掉 pyoutoui 的检测机制
        pyautogui.FAILSAFE = False
        pydirectinput.FAILSAFE = False
        # 游戏中等号状态
        running = False
        self.is_state = True
        print("game loop start")
        self._mylogs("game loop start")
        try:
            loopNumber = 0
            while self.is_state:
                loopNumber += 1
                random_sleep(5,10) # 随机化循环间隔
                if random.random() > 0.7:  # 偶尔进行无关鼠标移动
                    random_mouse_move()
                    random_sleep(0.5, 3)
                # 是否在主页
                if clash.find_image_all(images[GameState.HOME]) and self.is_state:
                    print("在主页")
                    self._mylogs("在主页")
                    # 找到开始游戏
                    result = clash.find_images_all(images[GameState.START])
                    if result:
                        print(f"Found image at screen coordinates: {result}")
                        move_and_click(result[0], result[1])

                # 是否在匹配状态
                if clash.find_image_all(images[GameState.LOADING]) and self.is_state:
                    print("匹配中")
                    self._mylogs("匹配中")
                # 是否在等待加入玩家状态
                if clash.find_image_all(images[GameState.LOADING1]) and self.is_state:
                    print("等待加入玩家")
                    self._mylogs("等待加入玩家")
                # 是否在游戏中
                if clash.find_image_all(images[GameState.GAME]) and self.is_state:
                    print("游戏中")
                    self._mylogs("游戏中")
                    random_sleep(5,10)
                    while clash.find_image_all(images[GameState.GAME]) and self.is_state:
                        # 按下f键
                        press_key(0x46)
                        random_sleep(1, 3)
                        # 按下=键
                        press_key(0xBB)
                        random_sleep(1, 3)
                        # 按下空格键
                        press_key(0x20)  # 按下空格键
                        random_sleep(1, 3)
                        # 单击鼠标左键
                        move_and_click(300, 300)  # 单击鼠标左键
                        random_sleep(4, 8)
                else:
                    # 判断是否有返回主页的按钮
                    if clash.find_images_all(images[GameState.BACKHOMEALL]) and self.is_state:
                        self._mylogs("返回主页中")
                        # 等待返回主页3并点击返回主页3
                        while self.is_state:
                            # 点击返回主页 返回至大厅
                            result = clash.find_image_all(images[GameState.BACKHOME1])
                            if result and self.is_state:
                                move_and_click(result[0], result[1])
                            random_sleep(0.6,1.5)
                            move_and_click(300, 300)
                            # 点击返回主页2 确认
                            result = clash.find_image_all(images[GameState.BACKHOME2])
                            if result and self.is_state:
                                move_and_click(result[0], result[1])
                            random_sleep(0.7, 1.5)
                            move_and_click(300, 300)
                            # 点击返回主页3 继续
                            if clash.find_image_all(images[GameState.BACKHOME3]) and self.is_state:
                                result = clash.find_image_all(images[GameState.BACKHOME3])
                                if result:
                                    move_and_click(result[0], result[1])
                            random_sleep(0.8, 1.4)
                            move_and_click(300, 300)
                            # 点击返回主页4mm 关闭
                            if clash.find_image_all(images[GameState.BACKHOME4]) and self.is_state:
                                result = clash.find_image_all(images[GameState.BACKHOME4])
                                if result:
                                    move_and_click(result[0], result[1])
                            random_sleep(0.4,0.8)
                            # 判断是否在主页
                            if clash.find_image_all(images[GameState.HOME]) and self.is_state:
                                break
                if self.is_state:
                    self._mylogs(f"第 {loopNumber} 次检查", 2)
        except Exception as e:
            self._mylogs("异常退出 请从新开启", 2)
        self._mylogs("game loop end")

    def getImagesMap(self):
        home = "./images/chi_sim/home.jpg"
        start = ["./images/chi_sim/start.jpg", "./images/chi_sim/start_act.jpg"]
        loading = "./images/chi_sim/loading.jpg"
        loading1 = "./images/chi_sim/loading1.jpg"
        game = "./images/chi_sim/game.jpg"
        backhome1 = "./images/chi_sim/backhome1.jpg"
        backhome2 = "./images/chi_sim/backhome2.jpg"
        backhome3 = "./images/chi_sim/backhome3.jpg"
        backhome4 = "./images/chi_sim/backhome4.jpg"
        home_1080 = "./images/chi_sim_1080/home.jpg"
        start_1080 = ["./images/chi_sim_1080/start.jpg", "./images/chi_sim_1080/start_act.jpg"]
        loading_1080 = "./images/chi_sim_1080/loading.jpg"
        loading1_1080 = "./images/chi_sim_1080/loading1.jpg"
        game_1080 = "./images/chi_sim_1080/game.jpg"
        backhome1_1080 = "./images/chi_sim_1080/backhome1.jpg"
        backhome2_1080 = "./images/chi_sim_1080/backhome2.jpg"
        backhome3_1080 = "./images/chi_sim_1080/backhome3.jpg"
        backhome4_1080 = "./images/chi_sim_1080/backhome4.jpg"
        home_4k = "./images/chi_sim_4k/home.jpg"
        start_4k = ["./images/chi_sim_4k/start.jpg", "./images/chi_sim_4k/start_act.jpg"]
        loading_4k = "./images/chi_sim_4k/loading.jpg"
        loading1_4k = "./images/chi_sim_4k/loading1.jpg"
        game_4k = "./images/chi_sim_4k/game.jpg"
        backhome1_4k = "./images/chi_sim_4k/backhome1.jpg"
        backhome2_4k = "./images/chi_sim_4k/backhome2.jpg"
        backhome3_4k = "./images/chi_sim_4k/backhome3.jpg"
        backhome4_4k = "./images/chi_sim_4k/backhome4.jpg"
        # 获取 ./images/chi_sim/home.jpg 绝对路径
        home = os.path.abspath(os.path.join(os.path.dirname(__file__), home))
        start = [os.path.abspath(os.path.join(os.path.dirname(__file__), item)) for item in start]
        loading = os.path.abspath(os.path.join(os.path.dirname(__file__), loading))
        loading1 = os.path.abspath(os.path.join(os.path.dirname(__file__), loading1))
        game = os.path.abspath(os.path.join(os.path.dirname(__file__), game))
        backhome1 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome1))
        backhome2 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome2))
        backhome3 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome3))
        backhome4 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome4))
        # 获取 ./images/chi_sim_1080/home.jpg 绝对路径
        home_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), home_1080))
        start_1080 = [os.path.abspath(os.path.join(os.path.dirname(__file__), item)) for item in start_1080]
        loading_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), loading_1080))
        loading1_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), loading1_1080))
        game_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), game_1080))
        backhome1_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome1_1080))
        backhome2_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome2_1080))
        backhome3_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome3_1080))
        backhome4_1080 = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome4_1080))
        # 获取 ./images/chi_sim_4k/home 绝对路径
        home_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), home_4k))
        start_4k = [os.path.abspath(os.path.join(os.path.dirname(__file__), item)) for item in start_4k]
        loading_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), loading_4k))
        loading1_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), loading1_4k))
        game_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), game_4k))
        backhome1_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome1_4k))
        backhome2_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome2_4k))
        backhome3_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome3_4k))
        backhome4_4k = os.path.abspath(os.path.join(os.path.dirname(__file__), backhome4_4k))


        # 获取当前屏幕宽度
        screen_width = pyautogui.size().width
        if screen_width >= 1920 and screen_width < 2560:
            return {
                "home": home_1080,
                "start": start_1080,
                "loading": loading_1080,
                "loading1": loading1_1080,
                "game": game_1080,
                "backhome1": backhome1_1080,
                "backhome2": backhome2_1080,
                "backhome3": backhome3_1080,
                "backhome4": backhome4_1080,
                "backhomeall": [backhome1_1080, backhome2_1080, backhome3_1080, backhome4_1080]
            }
        elif screen_width > 1920 and screen_width <= 2560:
            return {
                "home": home,
                "start": start,
                "loading": loading,
                "loading1": loading1,
                "game": game,
                "backhome1": backhome1,
                "backhome2": backhome2,
                "backhome3": backhome3,
                "backhome4": backhome4,
                "backhomeall": [backhome1, backhome2, backhome3, backhome4]
            }
        elif screen_width >2560:
            return {
                "home": home_4k,
                "start": start_4k,
                "loading": loading_4k,
                "loading1": loading1_4k,
                "game": game_4k,
                "backhome1": backhome1_4k,
                "backhome2": backhome2_4k,
                "backhome3": backhome3_4k,
                "backhome4": backhome4_4k,
                "backhomeall": [backhome1_4k, backhome2_4k, backhome3_4k, backhome4_4k]
            }

    def setState(self, state):
        self.is_state = state

    def getState(self):
        return self.is_state

    # 判断是否开启某个进程
    def isProcessRunning(self, processName):
        if os.system(f"tasklist | findstr {processName}"):
            return True
        else:
            return False

    # 通用日志方法
    def _mylogs(self, message, type=1):
        if type == 1:
            self.c(message)
        else:
            self.c2(message)

    def setCllback(self, c):
        self.c = c

    def setCllback2(self, c2):
        self.c2 = c2


if __name__ == '__main__':
    game = gameloop()
    getimg = ImageFinder()
    images = game.getImagesMap()
    # print(images[GameState.BACKHOME3])
    _images = "./images/test/1.jpg"
    print(_images)
    result = getimg.find_image_all(_images)
    pyautogui.moveTo(result[0], result[1])
    print(result)
