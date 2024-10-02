import time
from tkinter import *
from tkinter.ttk import *
from tkinter import Button as classical_Button
from win32gui import GetParent, SetWindowPos, UpdateWindow, SetWindowLong, GetWindowLong, ReleaseCapture, SendMessage
from win32con import NULL, SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_DRAWFRAME, GWL_STYLE, WS_CAPTION, WM_SYSCOMMAND, \
    SC_MOVE, HTCAPTION
from PIL import ImageGrab, Image
import threading
import cv2
import numpy as np
import os
import re
import keyboard as kb


class Entry_frame(Frame):
    # 该类继承Frame类
    def __init__(self, master, entry_var, left_label_text='', right_label_text='', **kw):
        '''
        :param master: 父控件
        :param entry_var: Entry控件关联的String变量
        :param left_label_text: Entry左边的文字
        :param right_label_text: Entry右边的文字
        :param kw:
        '''
        super().__init__(master)
        self.left_label = Label(self, text=left_label_text)
        self.entry = Entry(self, textvariable=entry_var)
        self.right_label = Label(self, text=right_label_text)

    def pack(self, cnf={}, **kw):
        super().pack(cnf, **kw)
        self.left_label.pack(side=LEFT)
        self.entry.pack(side=LEFT)
        self.right_label.pack(side=LEFT)


class StringVarFunc(StringVar):
    def __init__(self):
        super().__init__()
        self.press_release = BooleanVar()
        self.press_release.set(True)


class shot_Tl:
    def __init__(self, master):
        self.tl = Toplevel(master.master, bg='#add123')

        self.tl.wm_attributes('-transparentcolor', '#add123')
        self.tl.wm_attributes('-topmost', 'true')

        title_style = Style()
        title_style.configure("1.TFrame", background='grey', padx=0, pady=0, height=0)
        title = Frame(self.tl, style="1.TFrame", height=0)
        title.pack(side=TOP, fill=X, expand=0, padx=0, pady=0, ipadx=0, ipady=0)
        start_button = classical_Button(title, padx=0, pady=0, height=0, width=0, background='grey', text="●",
                                        font=('', 10),
                                        command=lambda: print())
        start_button.pack(side=RIGHT, fill='none', expand=0, ipadx=0, ipady=0, anchor=E)

        empty_style = Style()
        empty_style.configure("2.TFrame", background='#add123')
        empty_frame = Frame(self.tl, style="2.TFrame", takefocus=0)
        empty_frame.pack(side=TOP, expand=1, fill=BOTH)

        windowMove(title, self.tl)

        self.tl.after(1000, lambda: self.titlebar(self.tl))

        master.toplevel = self.tl
        master.tl_title = title
        master.tl_start_button = start_button

    def titlebar(self, window):
        hWnd = GetParent(window.winfo_id())
        SetWindowLong(hWnd, GWL_STYLE, GetWindowLong(hWnd, GWL_STYLE) & ~WS_CAPTION)
        SetWindowPos(hWnd, NULL, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_DRAWFRAME)
        UpdateWindow(hWnd)


def get_special_keyCode_list():
    list2 = []
    other = '''` 192
    - 189
    = 187
    [ 219
    ] 221
    ; 186
    ' 222
    \\ 220
    , 188
    . 190
    / 191'''

    list2.extend([int(i.split(' ')[-1]) for i in other.split('\n')])
    return list2


def get_common_keyCode_list():
    list1 = []
    list1.extend(list(range(65, 91)))
    list1.extend(list(range(48, 58)))
    list1.extend(list(range(96, 106)))
    list1.extend(list(range(112, 124)))

    list1.extend([111, 106, 109, 107, 110])
    list1.extend([111, 106, 109, 107, 110])
    list1.append(32)
    return list1


class App:

    def Var_create(self):
        # 运行状态
        self.State = BooleanVar()
        self.State.set(False)

        # 开始运行或结束运行的快捷键
        self.Fast_key = StringVarFunc()
        self.Fast_key.set('')

        # 是否要检测相似度 布尔值
        self.Detect_imgs = BooleanVar()
        self.Detect_imgs.set(True)

        # 相似度
        self.Min_similarity = StringVar()
        self.Min_similarity.set('0.4')

        # 是否要裁去相似部分 布尔值
        self.Cut = BooleanVar()
        self.Cut.set(True)

        # 图片拼接方向： 横向或竖向
        self.Join_direction = StringVar()
        # ['x','y']
        self.Join_direction.set('y')

        # 图片截取方式： 固定时间 或 不定时间
        self.Mode = StringVar()
        # [Regular,Change]
        self.Mode.set('Regular')

        # 固定时间的模式： 间隔固定的秒数截取 检测到固定变化的时间后转为第一种模式 根据音乐的配置按固定的时间截取
        self.Regular_mode = StringVar()
        # ['Seconds','Auto','Music']
        self.Regular_mode.set('Seconds')

        # 固定时间的数值大小
        self.Regular_time = StringVar()

        # 设定的检测固定时间的时间总长
        self.Full_time = StringVar()

        self.Paishu = StringVar()
        self.Paishu.set('4')
        self.Shizhi = StringVar()
        self.Shizhi.set('4')
        self.Bpm = StringVar()
        self.Bpm.set('120')
        self.Bars = StringVar()


        self.Change_mode = StringVar()
        # ['Test','Manual']
        self.Change_mode.set('Test')

        self.Test_time_interval = StringVar()

        self.Manual_fast_key = StringVarFunc()

        self.Setting_or_not = BooleanVar()
        self.Setting_or_not.set(False)

    def widget_create(self):

        def restrict_input(s: str) -> bool:
            if s:

                pattern = re.compile(r'^[1-9]\d*\.\d*$|^0\.\d*$|^[1-9]\d*$|^0$')
                # 开头为一到九种的一个数字 0到任意个数字 . 0到任意个数字  | 小数 | 0
                result = re.match(pattern, s)
                if result is not None:

                    return re.match(pattern, s).group() == s
                else:
                    return False

            else:
                return True

        def __start_frame():
            start_frame = Frame(self.master)
            start_frame.pack(side=TOP, fill=BOTH, expand=1, padx=6, pady=16)
            return start_frame

        def __start_button():
            start_button = Button(self.start_frame, text='开始捕捉', command=lambda: print())
            start_button.pack(side=LEFT, expand=1, ipady=3, ipadx=4)
            return start_button

        def __fast_key_entry():
            fast_key_frame = Entry_frame(self.start_frame, self.Fast_key, left_label_text='快捷键：')

            fast_key_frame.entry.config(justify=CENTER, width=7)
            self.Fast_key.trace("w", lambda *args: fast_key_frame.entry.config(
                width=len(self.Fast_key.get()) + 3))

            fast_key_frame.pack(side=LEFT, expand=1, fill=BOTH)
            return fast_key_frame.entry

        # （多选框）是否进行相似度检测【 相似度为多少截取 】  （多选框）合并图片时是否裁剪相同部分
        def __other_config_Labelframe():
            other_config_Labelframe = Labelframe(self.start_frame, text='其他设置')
            other_config_Labelframe.pack(side=LEFT, expand=1, fill=BOTH, padx=10, pady=6)
            return other_config_Labelframe

        def __detect_Similarity_frame():
            detect_Similarity_frame = Frame(self.other_config_frame)
            detect_Similarity_frame.pack(side=TOP, expand=1, fill=BOTH)
            return detect_Similarity_frame

        def __detect_Similarity_checkbutton():
            checkbutton = Checkbutton(self.detect_Similarity_frame, text='相似度检查', variable=self.Detect_imgs)
            checkbutton.pack(side=LEFT, fill=BOTH, padx=6, pady=3)
            return checkbutton

        def __detect_Similarity_entry():
            entry = Entry(self.detect_Similarity_frame, textvariable=self.Min_similarity)
            entry.config(justify=CENTER, width=7, validate="key",
                         validatecommand=(self.master.register(
                             lambda str1: True if not str1 else (
                                 re.match(r"^0\.\d*$|^0$", str1).group() == str1 if (re.match(
                                     r"^0\.\d*$|^0$", str1)) is not None else False)), "%P"))
            entry.pack(side=LEFT)
            return entry

        def __cut_pics_checkbutton():
            cut_pics_checkbutton = Checkbutton(self.other_config_frame, text='合并图片时是否裁去相同部分', variable=self.Cut)
            cut_pics_checkbutton.pack(side=TOP, fill=BOTH, padx=6, pady=3, expand=1)
            return cut_pics_checkbutton

        def __join_direction_labelframe():
            join_direction_labelframe = Labelframe(self.master, text='拼接方向')
            join_direction_labelframe.pack(side=TOP, fill=BOTH, expand=1, padx=10, pady=6)
            return join_direction_labelframe

        def __shu_radiobutton():
            shu_radiobutton = Radiobutton(self.join_direction_labelframe, text='竖向', value='y',
                                          variable=self.Join_direction)
            shu_radiobutton.pack(side=LEFT, fill=BOTH, expand=1, padx=6, pady=3)
            return shu_radiobutton

        def __heng_radiobutton():
            heng_radiobutton = Radiobutton(self.join_direction_labelframe, text='横向', value='x',
                                           variable=self.Join_direction)
            heng_radiobutton.pack(side=RIGHT, fill=BOTH, expand=1, padx=6, pady=3)
            return heng_radiobutton

        def __time_interval_labelframe():
            time_interval_labelframe = Labelframe(self.master, text='捕捉的时间间隔')
            time_interval_labelframe.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=6)
            return time_interval_labelframe

        def __left_frame():
            left_paned = Frame(self.time_interval_labelframe)
            left_paned.pack(side=LEFT, expand=1, fill=BOTH, padx=6, pady=3)
            return left_paned

        def __regular_radiobutton():
            regular_radiobutton = Radiobutton(self.left_frame, text='固定时间', value='Regular', variable=self.Mode,
                                              command=self.change_state)
            regular_radiobutton.pack(side=TOP, fill=BOTH)

            return regular_radiobutton

        def __regular_frame():
            regular_frame = Frame(self.left_frame, relief=GROOVE, borderwidth=5)
            regular_frame.pack(side=TOP, expand=1, fill=BOTH)
            return regular_frame

        def __seconds_frame():
            seconds_paned = Frame(self.regular_frame)
            seconds_paned.pack(side=TOP, expand=1, fill=BOTH)
            return seconds_paned

        def __seconds_radiobutton():
            seconds_radiobutton = Radiobutton(self.seconds_frame, value='Seconds', variable=self.Regular_mode)
            seconds_radiobutton.pack(side=LEFT, fill=BOTH)
            return seconds_radiobutton

        def __seconds_entry():
            seconds_entry = Entry_frame(self.seconds_frame, left_label_text='每', right_label_text='s捕捉一张',
                                        entry_var=self.Regular_time)
            seconds_entry.entry.configure(width=7, justify=CENTER, validate="key",
                                          validatecommand=(self.master.register(restrict_input), "%P"))
            seconds_entry.pack(side=LEFT, expand=1, fill=BOTH)

            return seconds_entry.entry

        def __auto_seconds_frame():
            auto_seconds_paned = Frame(self.regular_frame)
            auto_seconds_paned.pack(side=TOP, expand=1, fill=BOTH)
            return auto_seconds_paned

        def __auto_seconds_radiobutton():
            auto_seconds_radiobutton = Radiobutton(self.auto_seconds_frame, text=' 自动测定切换时间', value='Auto',
                                                   variable=self.Regular_mode)
            auto_seconds_radiobutton.pack(side=TOP, fill=BOTH)
            return auto_seconds_radiobutton

        def __auto_full_time_entry():
            auto_full_time_frame = Entry_frame(self.auto_seconds_frame, entry_var=self.Full_time,
                                               left_label_text='     识别总时长',
                                               right_label_text='s')
            auto_full_time_frame.entry.configure(width=7, justify=CENTER, validate="key",
                                                 validatecommand=(self.master.register(restrict_input), "%P"))
            auto_full_time_frame.pack(side=TOP, fill=BOTH, expand=1)
            return auto_full_time_frame.entry

        def __musical_type_frame():
            musical_type_paned = Frame(self.regular_frame)
            musical_type_paned.pack(side=TOP, expand=1, fill=BOTH)
            return musical_type_paned

        def __musical_type_radiobutton():
            musical_type_radiobutton = Radiobutton(self.musical_type_frame, text=' 音乐类型', value='Music',
                                                   variable=self.Regular_mode)
            musical_type_radiobutton.pack(side=TOP, fill=BOTH)
            return musical_type_radiobutton

        def __related_music_setting_frame():
            related_music_setting_frame = Frame(self.musical_type_frame, relief=GROOVE, borderwidth=5)
            related_music_setting_frame.pack(side=TOP, fill=BOTH, expand=1)
            return related_music_setting_frame

        def __music_paihao_frame():
            music_paihao_frame = Frame(self.related_music_setting_frame)
            music_paihao_frame.pack(side=TOP, fill=BOTH, expand=True)
            return music_paihao_frame

        def __music_paishu_entry():
            music_paishu_frame = Entry_frame(self.music_paihao_frame, left_label_text='拍号：',
                                             entry_var=self.Paishu, right_label_text='/')
            music_paishu_frame.entry.configure(width=5, validate="key",
                                               validatecommand=(self.master.register(
                                                   lambda str1: True if not str1 else (
                                                       re.match(r"^[1-9]\d*$", str1).group() == str1 if (re.match(
                                                           r"^[1-9]\d*$", str1)) is not None else False)), "%P"),

                                               justify=CENTER)
            music_paishu_frame.pack(side=LEFT, fill=BOTH)

            return music_paishu_frame.entry

        def __music_shizhi_combobox():
            music_shizhi_combobox = Combobox(self.music_paihao_frame,
                                             values=['1', '2', '4', '8', '16', '32', '64', '128'],
                                             state="readonly", textvariable=self.Shizhi)
            music_shizhi_combobox.configure(width=3)
            music_shizhi_combobox.pack(side=LEFT, fill=BOTH)
            return music_shizhi_combobox

        def __music_bpm_entry():
            music_bpm_frame = Entry_frame(self.related_music_setting_frame, left_label_text='速度：',
                                          right_label_text='bpm',
                                          entry_var=self.Bpm)
            music_bpm_frame.entry.configure(width=7, justify=CENTER, validate="key",
                                            validatecommand=(self.master.register(restrict_input), "%P"))

            music_bpm_frame.pack(side=TOP, fill=BOTH, expand=True)
            return music_bpm_frame.entry

        def __include_bars_entry():
            include_bars_frame = Entry_frame(self.related_music_setting_frame, left_label_text='一次捕捉中的一行包含',
                                             right_label_text='个小节',
                                             entry_var=self.Bars)
            include_bars_frame.entry.configure(width=7, justify=CENTER, validate="key",
                                               validatecommand=(self.master.register(restrict_input), "%P"))

            include_bars_frame.pack(side=TOP, fill=BOTH, expand=True)
            return include_bars_frame.entry

        def __right_frame():
            right_paned = Frame(self.time_interval_labelframe)
            right_paned.pack(side=LEFT, fill=BOTH, expand=1, padx=6, pady=3)
            return right_paned

        def __change_time_radiobutton():
            change_time_radiobutton = Radiobutton(self.right_frame, text='不定时间', value='Change', variable=self.Mode,
                                                  command=self.change_state)
            change_time_radiobutton.pack(side=TOP, fill=BOTH)
            return change_time_radiobutton

        def __change_time_frame():
            change_time_frame = Frame(self.right_frame, relief=GROOVE, borderwidth=5)
            change_time_frame.pack(side=TOP, fill=BOTH, expand=True)
            return change_time_frame

        def __text_seconds_frame():
            paned = Frame(self.change_time_frame)
            paned.pack(side=TOP, fill=BOTH, expand=1)
            return paned

        def __test_seconds_radiobutton():
            radio = Radiobutton(self.text_seconds_frame, text=' 测定变化，变化即截取', variable=self.Change_mode, value='Test')
            radio.pack(side=TOP, fill=BOTH, expand=1)
            return radio

        def __test_seconds_entry():
            test_seconds_frame = Entry_frame(self.text_seconds_frame, left_label_text='     每',
                                             right_label_text='s进行一次测试',
                                             entry_var=self.Test_time_interval)
            test_seconds_frame.entry.configure(width=7, justify=CENTER, validate="key",
                                               validatecommand=(self.master.register(restrict_input), "%P"))
            test_seconds_frame.pack(side=TOP, fill=BOTH, expand=1)
            return test_seconds_frame.entry

        def __manual_frame():
            paned = Frame(self.change_time_frame)
            paned.pack(side=TOP, expand=1, fill=BOTH)
            return paned

        def __manual_radiobutton():
            radio = Radiobutton(self.manual_frame, text=' 手动', variable=self.Change_mode, value='Manual')
            radio.pack(side=TOP, fill=BOTH, expand=1)
            return radio

        def __manual_fastKey_entry():
            frame = Entry_frame(self.manual_frame, entry_var=self.Manual_fast_key, left_label_text='     快捷键：')
            frame.entry.configure(justify=CENTER, width=7)

            self.Manual_fast_key.trace("w", lambda *args: frame.entry.config(
                width=len(self.Manual_fast_key.get()) + 3))

            frame.pack(side=TOP, fill=BOTH, expand=1)
            return frame.entry

        self.start_frame = __start_frame()
        self.start_button = __start_button()
        self.fast_key_entry = __fast_key_entry()

        self.other_config_frame = __other_config_Labelframe()
        self.detect_Similarity_frame = __detect_Similarity_frame()
        self.detect_Similarity_checkbutton = __detect_Similarity_checkbutton()
        self.detect_Similarity_entry = __detect_Similarity_entry()
        self.cut_pics_checkbutton = __cut_pics_checkbutton()

        self.join_direction_labelframe = __join_direction_labelframe()
        self.shu_radiobutton = __shu_radiobutton()
        self.heng_radiobutton = __heng_radiobutton()

        # 捕捉的时间间隔
        self.time_interval_labelframe = __time_interval_labelframe()

        self.left_frame = __left_frame()

        self.regular_radiobutton = __regular_radiobutton()
        self.regular_frame = __regular_frame()

        self.seconds_frame = __seconds_frame()
        self.seconds_radiobutton = __seconds_radiobutton()
        self.seconds_entry = __seconds_entry()

        self.auto_seconds_frame = __auto_seconds_frame()
        self.auto_seconds_radiobutton = __auto_seconds_radiobutton()
        self.auto_full_time_entry = __auto_full_time_entry()

        self.musical_type_frame = __musical_type_frame()
        self.musical_type_radiobutton = __musical_type_radiobutton()
        self.related_music_setting_frame = __related_music_setting_frame()

        self.music_paihao_frame = __music_paihao_frame()

        self.music_paishu = __music_paishu_entry()
        self.music_shizhi = __music_shizhi_combobox()
        self.music_bpm_entry = __music_bpm_entry()
        self.include_bars_entry = __include_bars_entry()

        self.right_frame = __right_frame()

        self.change_time_radiobutton = __change_time_radiobutton()
        self.change_time_frame = __change_time_frame()

        self.text_seconds_frame = __text_seconds_frame()
        self.test_seconds_radiobutton = __test_seconds_radiobutton()
        self.test_seconds_entry = __test_seconds_entry()

        self.manual_frame = __manual_frame()
        self.manual_radiobutton = __manual_radiobutton()

        self.manual_fastKey_entry = __manual_fastKey_entry()

        self.change_state()

    def __init__(self, master, testPics_path, joinPicsWork_path, output_path):
        self.master: Tk = master

        self.__win()

        self.root_path = os.path.dirname(__file__)
        self.testPics_path = testPics_path
        self.joinPicsWork_path = joinPicsWork_path
        self.output_path = output_path

        self.width = -1
        self.height = -1

        self.common_keyCode_list = get_common_keyCode_list()
        self.special_keyCode_list = get_special_keyCode_list()

        self.Var_create()

        self.widget_create()

        # 鼠标按键事件触发 传入manage函数中调用
        self.master.bind_all('<Button>', self.manage)

        self.fast_key_entry.bind('<KeyRelease>', lambda event: self.set_fast_key(event, var=self.Fast_key, func=lambda
            Var: self.start_and_stop_at_second_time(Var) if not self.Setting_or_not.get() else print('not allow')))
        self.fast_key_entry.bind('<BackSpace>',
                                 lambda event: 'break')
        self.fast_key_entry.bind('<Delete>',
                                 lambda event: 'break')

        # self.manual_fastKey_entry.bind('<KeyRelease>',
        #                                lambda event: self.set_fast_key(event, var=self.Manual_fast_key,
        #                                                                func=self.start_and_stop_at_second_time))
        self.manual_fastKey_entry.bind('<KeyRelease>',
                                       lambda event: self.set_fast_key(event, var=self.Manual_fast_key,
                                                                       func=lambda Var: Var.press_release.set(False)))
        self.manual_fastKey_entry.bind('<BackSpace>',
                                       lambda event: 'break')
        self.manual_fastKey_entry.bind('<Delete>',
                                       lambda event: 'break')

        # 在Entry控件中，键盘按键松开事件传入manage
        self.fast_key_entry.bind_class('TEntry', '<KeyRelease>', self.manage, add='+')

        # self.fast_key_entry.bind_class('TEntry', '<FocusIn>', lambda x: self.Setting_or_not.set(True), add='+')
        # self.fast_key_entry.bind_class('TEntry', '<FocusOut>', lambda x: self.Setting_or_not.set(False), add='+')
        # 防止在设置快捷键时按下与原来相同的快捷键导致启动操作
        self.fast_key_entry.bind('<FocusIn>', lambda x: self.Setting_or_not.set(True), add='+')
        self.fast_key_entry.bind('<FocusOut>', lambda x: self.Setting_or_not.set(False), add='+')

        self.manual_fastKey_entry.bind('<FocusIn>', lambda x: self.Setting_or_not.set(True), add='+')
        self.manual_fastKey_entry.bind('<FocusOut>', lambda x: self.Setting_or_not.set(False), add='+')
        # 阻止按键的默认操作
        self.fast_key_entry.bind('<Key>', lambda x: 'break', add='+')
        self.manual_fastKey_entry.bind('<Key>', lambda x: 'break', add='+')

    def __win(self):
        pass

    def change_state(self):
        all_regular_list = self.regular_frame.winfo_children()
        all_change_list = self.change_time_frame.winfo_children()
        mode = self.Mode.get()
        if mode == 'Regular':
            state = [NORMAL, DISABLED]
        else:
            state = [DISABLED, NORMAL]

        for i in all_regular_list:
            try:
                i.config(state=state[0])
            except Exception:
                pass
            else:
                if i == self.music_shizhi:
                    # 使combobox只读，不能写入
                    if state[0] == NORMAL:
                        i.configure(state='readonly')

            if i.winfo_children():
                all_regular_list.extend(i.winfo_children())

        for n in all_change_list:
            try:
                n.config(state=state[1])
            except Exception:
                pass
            if n.winfo_children():
                all_change_list.extend(n.winfo_children())

    # 程序框上显示相似度
    def show_similarity(self, str1=''):
        if str1:
            self.master.wm_title(f'截图拼接  相似度：{str1}')
        else:
            self.master.wm_title(f'截图拼接')

    def get_regular_time(self):
        # ['Seconds', 'Auto', 'Music']

        if self.Regular_mode.get() == 'Seconds':
            self.tl_start_button.configure(background='red')

            return float(self.Regular_time.get())

        elif self.Regular_mode.get() == 'Auto':
            self.tl_start_button.configure(background='yellow')

            testPics_path = self.testPics_path

            size = (self.tl_title.winfo_width(), self.toplevel.winfo_height() - self.tl_title.winfo_height())
            # 录制区域的大小。（宽度,高度）

            site = (
                self.toplevel.winfo_x() + 7,
                self.toplevel.winfo_y() + self.tl_title.winfo_height() + 7)  # 7是win7边框宽度
            # 录制区域的左上角的坐标

            img_bbox = (site[0], site[1], site[0] + size[0], site[1] + size[1])
            # 图片 左，上，右，下 的x=?划分截取区域的坐标

            is_first = True

            testFullTime = float(self.Full_time.get())
            regular_time = 0.0

            similaritys = 1.0

            first_pic_path = os.path.join(testPics_path, 'First.jpg')
            comparison_path = os.path.join(testPics_path, 'comparison.jpg')

            start_time = time.perf_counter()
            end_time = time.perf_counter()

            while (end_time - start_time <= testFullTime) and self.State.get():
                # ①识别总时长超过设定时间，识别失败 while停止是因为超时，且没有break。State仍为True
                # ②按下停止按键或快捷键，终止识别 while停止是因为按下暂停,且没有break，设置了State为False。

                # ③识别出固定的时间长度，终止识别 并设定固定时间模式 并设定固定时间长度

                img = ImageGrab.grab(bbox=img_bbox)  # bbox 定义左、上、右和下像素的4元组
                img.save(comparison_path)

                if is_first:

                    img.save(first_pic_path)

                    is_first = False

                else:
                    similaritys = similarity(first_pic_path, comparison_path)
                    self.show_similarity(similaritys)
                    # 程序框上显示相似度
                    print(similaritys)
                    # 要识别相似度
                    if self.Detect_imgs.get():
                        # 相似度低于一定值即判定发生指定程度的变化，停止识别并设定固定时间
                        if similaritys < float(self.Min_similarity.get()):

                            self.tl_start_button.configure(background='grey')
                            windowMove(self.tl_title, self.toplevel)
                            self.State.set(False)

                            regular_time = end_time - start_time
                            self.Regular_mode.set('Seconds')
                            self.Regular_time.set(f'{regular_time}')
                            break

                    # 不识别相似度
                    else:
                        #发生变化，停止识别并设定固定时间
                        if similaritys != 1.0:

                            self.tl_start_button.configure(background='grey')
                            windowMove(self.tl_title, self.toplevel)
                            self.State.set(False)

                            regular_time = end_time - start_time
                            self.Regular_mode.set('Seconds')
                            self.Regular_time.set(f'{regular_time}')
                            break

                end_time = time.perf_counter()

            else:
                # 只有   按下停止   和  超时  才会进入以下程序块
                # State: False       True
                if self.State.get():
                    self.Full_time.set('')
                    self.State.set(False)
                    self.show_similarity()
                    self.switch_widget_state(True)
                    self.tl_start_button.configure(background='grey')
                    windowMove(self.tl_title, self.toplevel)
                else:
                    self.show_similarity()
                    self.switch_widget_state(True)
                    self.tl_start_button.configure(background='grey')
                    windowMove(self.tl_title, self.toplevel)

        # 按音乐类型的bpm等返回截图的固定时间
        else:
            return float(self.Bpm.get()) / (float(float(self.Paishu.get()) * float(self.Bars.get())))

    def got_RGBA(self, picPath):
        # 一列列读取，从上到下从左向右

        img = Image.open(picPath)

        width, height = img.size

        if self.width != width or self.height != height:
            self.width = width
            self.height = height
        img = img.convert('RGBA')
        iarray = []
        # iarray:
        #

        # [[(),(),(),(),(),(),(),(),(),()],
        #  [(),(),(),(),(),(),(),(),(),()],
        #  [(),(),(),(),(),(),(),(),(),()],
        #  [(),(),(),(),(),(),(),(),(),()],
        #  [(),(),(),(),(),(),(),(),(),()],]

        # ()为颜色的rgba值:(r,g,b,a)

        # iarray[3][4] 为图片中第四行第五列的像素的rgba值

        # 在iarray添加每一行的[],[]内含该行所有像素的rgba值，即()

        for i in range(height):
            iarray.append([])
        # 该过程从上到下逐行从左向右读取像素rgba值

        for i in range(height):
            for j in range(width):
                r, g, b, a = img.getpixel((j, i))

                rgba = (r, g, b, a)

                iarray[i].append(rgba)
        if self.Join_direction.get() == 'y':

            return np.array(iarray)
        else:
            return np.rot90(np.array(iarray), -1)

    # 程序运行越来越快的原因：
    # 操作系统会将经常使用的文件从磁盘缓存到 RAM。RAM访问比磁盘访问快得多。
    # 多次运行python后，内存温暖，OS 可以从快速 RAM 加载相关文件。经过两三次后，它达到最快。

    #   横向  拼接相同图片，开启裁剪相同部分选项，会有部分未切，不知道什么原因

    def image_Splicing(self):
        # 三维数组

        allPicsArraylist = []
        allPicsPath = self.joinPicsWork_path
        output_path = self.output_path
        height = self.height
        splitIndex = 0
        same = False

        for pic1 in os.listdir(allPicsPath):
            allPicsArraylist.append(self.got_RGBA(os.path.join(allPicsPath, pic1)))

        # 两张两张图片选取，
        # 通过对比第一张和第二张图片，找出相同的行数和在两张图片的位置，
        # 再删去第二张图片相同的部分最后合并至输出图片的ndarray数组对象里(outputPic)

        for i in range(len(allPicsArraylist)):
            firstPic = allPicsArraylist[i]

            # 如果firstPic对应的图片为第一张图片，则将firstPic拷贝作为输出图片的ndarray数组对象的初始值
            if i == 0:
                outputPic = firstPic.copy()

            # 如果firstPic对应的图片为最后一张图片，则结束程序完成拼接，将outputPic保存为图片，
            # 不是则将第二张图片的ndarray赋值给secondPic
            if i + 1 == len(allPicsArraylist):
                if self.Join_direction.get() == 'y':

                    im = Image.fromarray(np.uint8(outputPic))
                else:

                    im = Image.fromarray(np.uint8(np.rot90(outputPic, 1)))

                im.save(os.path.join(output_path, 'output.png'))

                self.switch_widget_state(True)
                self.tl_start_button.configure(background='grey')
                windowMove(self.tl_title, self.toplevel)

                return
            else:
                secondPic = allPicsArraylist[i + 1]
            # 识别相同行，并找出位置，切割后一张图片
            # 如果两张图片有相同行数的，位置不定或相同的区域，那么删去第二张图片上方相同的区域，剩下的拼接到第一张图片上

            # 假定两张图片相同的行数从1到图片总行数一个个尝试

            if self.Cut.get():

                for sameLines in range(1, height + 1):
                    # 已经找出相同部分并截取合并了，不用继续找了，因此直接break结束

                    if same:
                        same = False
                        splitIndex = 0
                        break
                    # 第一张图片从尾开始向下截取

                    for line1 in range(height, 0, -sameLines):
                        if line1 - sameLines < 0:
                            continue
                        firLine = firstPic[line1 - sameLines:line1, :, :]

                        # 第二张图片从头开始向上截取
                        for line2 in range(0, height, sameLines):

                            if line2 + sameLines > height:
                                continue
                            secline = secondPic[line2:line2 + sameLines, :, :]
                            if (firLine == secline).all():
                                # 判断相同部分是否唯一，不是则说明相同部分不完全.
                                # 也不需要用第一张图片截取的部分继续在第二张图片对比了，
                                # 因为已经确认第一张图片的这一部分与第二种图片有相同部分，但是不完全.

                                if same:
                                    splitIndex = 0
                                    same = False
                                    break

                                else:
                                    splitIndex = line2
                                    same = True
                        # 只有相同部分唯一才会合并

                        else:
                            if same:
                                splitIndex = splitIndex + sameLines
                                outputPic = np.concatenate((outputPic, secondPic[splitIndex:, :, :]), axis=0)
                                break

                # 两张图片完全不一样，直接合并
                else:
                    outputPic = np.concatenate((outputPic, secondPic[:, :, :]), axis=0)
            else:
                outputPic = np.concatenate((outputPic, secondPic[:, :, :]), axis=0)

    def one_start(self, times):
        # 固定时间截取
        joinPicsWork_path = self.joinPicsWork_path

        size = (self.tl_title.winfo_width(), self.toplevel.winfo_height() - self.tl_title.winfo_height())

        site = (
            self.toplevel.winfo_x() + 7, self.toplevel.winfo_y() + self.tl_title.winfo_height() + 7)  # 7是win7边框宽度

        img_bbox = (site[0], site[1], site[0] + size[0], site[1] + size[1])

        img_name = 1

        while self.State.get():
            img = ImageGrab.grab(bbox=img_bbox)  # bbox 定义左、上、右和下像素的4元组

            img.save(os.path.join(joinPicsWork_path, f'{img_name}.jpg'))
            img_name += 1
            time.sleep(times)

    def two_start(self):
        # 检测不相似程度，低于一定值则截取
        self.tl_start_button.configure(background='blue')

        size = (self.tl_title.winfo_width(), self.toplevel.winfo_height() - self.tl_title.winfo_height())

        site = (
            self.toplevel.winfo_x() + 7,
            self.toplevel.winfo_y() + self.tl_title.winfo_height() + 7)  # 7是win7边框宽度

        img_bbox = (site[0], site[1], site[0] + size[0], site[1] + size[1])

        is_first = True

        testTime = float(self.Test_time_interval.get())

        similaritys = 1.0

        testPics_path = self.testPics_path

        joinPicsWork_path = self.joinPicsWork_path
        first_pic_path = os.path.join(testPics_path, 'First.jpg')
        comparison_path = os.path.join(testPics_path, 'comparison.jpg')

        img_name = 1

        while self.State.get():
            self.tl_start_button.configure(background='blue')
            img = ImageGrab.grab(bbox=img_bbox)  # bbox 定义左、上、右和下像素的4元组
            img.save(comparison_path)

            if is_first:

                img.save(first_pic_path)
                img.save(os.path.join(joinPicsWork_path, '1.jpg'))
                img_name += 1

                is_first = False

            else:

                similaritys = similarity(first_pic_path, comparison_path)
                print(similaritys)
                self.show_similarity(similaritys)

                if similaritys < 0.8:
                    self.tl_start_button.configure(background='green')

                    img.save(first_pic_path)
                    img.save(os.path.join(joinPicsWork_path, f'{img_name}.jpg'))
                    img_name += 1

            time.sleep(testTime)

    def three_start(self):

        self.tl_start_button.configure(background='purple')

        size = (self.tl_title.winfo_width(), self.toplevel.winfo_height() - self.tl_title.winfo_height())

        site = (
            self.toplevel.winfo_x() + 7,
            self.toplevel.winfo_y() + self.tl_title.winfo_height() + 7)  # 7是win7边框宽度

        img_bbox = (site[0], site[1], site[0] + size[0], site[1] + size[1])

        joinPicsWork_path = self.joinPicsWork_path

        press = False

        img_name = 1

        while self.State.get():
            self.tl_start_button.configure(background='purple')

            if not self.Manual_fast_key.press_release.get():
                self.tl_start_button.configure(background='pink')
                img = ImageGrab.grab(bbox=img_bbox)  # bbox 定义左、上、右和下像素的4元组
                img.save(os.path.join(joinPicsWork_path, f'{img_name}.jpg'))
                img_name += 1

                self.Manual_fast_key.press_release.set(True)

    def switch_widget_state(self, cnf):
        children = self.master.winfo_children()
        if cnf:
            state = NORMAL
            self.start_button.configure(text='开始捕捉')
        else:
            state = DISABLED
            self.start_button.configure(text='停止')

        for i in children:
            try:
                i.configure(state=state)
            except Exception:
                children.extend(i.winfo_children())
            else:
                if i.winfo_class() in ('TButton', 'Button'):
                    # 界面和录制边框上的开始按钮还是设为NORMAL，预留了有停止的功能。但在合并图片开始设为DISABLED。

                    i.configure(state=NORMAL)
                if i == self.music_shizhi:
                    # 使combobox只读，不能写入
                    if state == NORMAL:
                        i.configure(state='readonly')

    def start_and_stop_at_second_time(self, var1_or_event):
        # 该函数依靠界面或录制窗口上的按钮、快捷键来调用

        # 运行状态   运行中或已结束

        # 开始判断State，确定处于什么状态
        # State的设定是用于停止还在截取或识别的程序（主要）和设置运行状态

        if self.State.get():
            self.State.set(False)
            self.show_similarity()

            if self.Mode.get() == 'Regular':

                if self.Regular_mode.get() == 'Auto':
                    print('Auto')
                    self.switch_widget_state(True)
                    self.tl_start_button.configure(background='grey')
                    windowMove(self.tl_title, self.toplevel)

                else:
                    self.start_button.configure(state=DISABLED)
                    self.tl_start_button.configure(state=DISABLED)

                    thread_it(self.image_Splicing)

            else:
                self.start_button.configure(state=DISABLED)
                self.tl_start_button.configure(state=DISABLED)
                thread_it(self.image_Splicing)

        else:
            # path = ['./test/', './work/', './output/']

            path = [self.testPics_path, self.joinPicsWork_path, self.output_path]

            for i in path:

                for file_name in os.listdir(i):
                    os.remove(os.path.join(i, file_name))
            self.State.set(True)
            stopMove(self.tl_title)
            self.switch_widget_state(False)

            if self.Mode.get() == 'Regular':

                if self.Regular_mode.get() in ('Seconds', 'Music'):
                    thread_it(lambda: self.one_start(self.get_regular_time()))

                elif self.Regular_mode.get() == 'Auto':
                    thread_it(self.get_regular_time)


            else:
                if self.Change_mode.get() == 'Test':
                    thread_it(self.two_start)

                else:
                    thread_it(self.three_start)

    def set_fast_key(self, event1: Event, var: StringVarFunc, func):
        # 数码锁定、滚动锁定大小写锁定会影响state

        # 绑定时应不触发原有的快捷键功能

        # 绑定时识别是否与现有快捷键重复，若是，则取消

        state = event1.state
        origin_fastKey_name = var.get()
        print(origin_fastKey_name)
        fastKey_name = ''

        if event1.keycode in self.common_keyCode_list + self.special_keyCode_list:

            if event1.keycode in self.common_keyCode_list:
                name = event1.keysym
            else:
                name = event1.char

            if state == 8:
                fastKey_name = name

            elif state == 9:
                fastKey_name = f'Shift + {name}'

            elif state == 12:
                fastKey_name = f'Ctrl + {name}'

            elif state == 13:
                fastKey_name = f'Ctrl + Shift + {name}'

            elif state == 131080:
                fastKey_name = f'Alt + {name}'

            elif state == 131081:
                fastKey_name = f'Shift + Alt + {name}'

            elif state == 131084:
                fastKey_name = f'Ctrl + Alt + {name}'

            if fastKey_name == self.Fast_key.get() or fastKey_name == self.Manual_fast_key.get():
                # 如果按下的快捷键与原有的或另一个冲突，则保持不变
                var.set(origin_fastKey_name)

            else:
                if origin_fastKey_name:
                    # 如果原本存在快捷键则删除
                    kb.remove_hotkey(origin_fastKey_name)

                var.set(fastKey_name)

                kb.add_hotkey(fastKey_name, lambda: func(var))

                # 原本的
                # 当按键松开，变量状态被设置为 松开
                # self.master.bind_all(var.releaseEvent, lambda events: var.press_release.set(True))

                self.master.focus_set()

        return 'break'

    def manage(self, event: Event):
        """

        :param event: Event对象 有两种 一种是鼠标按键事件 另一种是在Entry中的键盘释放事件
        :return: None
        """

        try:
            # 获取事件发生在什么控件的控件类型
            print(event.widget)
            print(event.widget.winfo_class())
        except AttributeError:
            return

        if event.widget.winfo_class() in ('TButton', 'Button'):
            self.start_and_stop_at_second_time(event)

        # 使在entry内按下enter可以使焦点回到根上
        # 和 鼠标按键 在entry或 列表选择框 或 文本 上按下时可以选中离它最近的单选按钮
        elif event.widget.winfo_class() in ('TEntry', 'TCombobox', 'TLabel'):
            if event.widget.winfo_class() == 'TEntry':
                if event.keysym == 'Return':
                    self.master.focus_set()

            widget = event.widget

            children = widget.master.winfo_children()

            while 'TRadiobutton' not in [i.winfo_class() for i in children]:
                widget = widget.master

                # 以下怀疑有问题，但实际运行没事，就不理了
                try:
                    children = widget.master.winfo_children()
                except Exception:
                    print(True)
                    return
            else:
                for n in children:
                    if n.winfo_class() == 'TRadiobutton':
                        n.invoke()

        else:
            self.master.focus_set()


def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()


def similarity(img11, img22):
    def cmpHash(hash11, hash22, shape=(10, 10)):
        nn = 0
        # hash长度不同则返回-1代表传参出错

        if len(hash11) != len(hash22):
            return -1

        for i in range(len(hash11)):
            # 相等则n计数+1，n最终为相似度

            if hash11[i] == hash22[i]:
                nn = nn + 1
        return nn / (shape[0] * shape[1])

    # 均值哈希算法
    def aHash(img111, shape=(10, 10)):

        # 缩放为10*10
        img111 = cv2.resize(img111, shape)

        # 转换为灰度图
        gray = cv2.cvtColor(img111, cv2.COLOR_BGR2GRAY)
        # s为像素和初值为0，hash_str为hash值初值为''
        s = 0
        hash_str = ''
        # 遍历累加求像素和
        for i in range(shape[0]):
            for j in range(shape[1]):
                s = s + gray[i, j]

        # 求平均灰度
        avg = s / 100

        # 灰度大于平均值为1相反为0生成图片的hash值
        for i in range(shape[0]):
            for j in range(shape[1]):
                if gray[i, j] > avg:
                    hash_str = hash_str + '1'
                else:
                    hash_str = hash_str + '0'
        return hash_str

    img1 = cv2.imread(img11)
    img2 = cv2.imread(img22)

    hash1111 = aHash(img1)
    hash2222 = aHash(img2)
    n = cmpHash(hash1111, hash2222)
    return n


def windowMove(widget, window):
    def move():
        ReleaseCapture()
        SendMessage(GetParent(window.winfo_id()), WM_SYSCOMMAND, SC_MOVE + HTCAPTION, 0)

    widget.bind("<B1-Motion>", lambda event: move())


def stopMove(widget):
    widget.unbind("<B1-Motion>")


if __name__ == '__main__':
    tk = Tk()
    root = App(tk, '.\\test', '.\\work', '.\\output')
    shot_Tl(root)
    tk.mainloop()
