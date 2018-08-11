from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from functools import partial
from random import randint as r
import numpy as np
from pprint import pprint
from kivy.uix.image import AsyncImage



class MainLayout(BoxLayout):
    #new functions
    def open_options(self,instance):
        self.clear_widgets()
        Window.size = (300, 400)
        self.add_widget(self.option_layout_main)
    def confirm_change(self,instance):
        self.nrows = int(self.option_ui_nrows.text)
        self.ncols = int(self.option_ui_ncols.text)
        self.ncolors = int(self.option_ui_color.text)
        self.color_dict = self.color_bank[:self.ncolors]
    #old functions
    def button_action(self, i, j, *largs):
        # print(len(self.e_list))
        if self.click_count % 2 == 0:
            # highlight the button, simpler way
            self.btn_matrix[i][j].background_color[3] = 1
            self.click_record = [i,j]
        else:
            last_position = self.click_record
            error = abs(last_position[0]-i)+abs(last_position[1]-j)
            #reset jewels to default alpha
            self.btn_matrix[i][j].background_color[3] = self.btn_alpha
            self.btn_matrix[last_position[0]][last_position[1]].background_color[3] = self.btn_alpha
            if error == 1:
                # switch two buttons
                self.switch_button(last_position,[i,j])
                self.check_board()
                if self.is_finished == True:
                    self.switch_button(last_position,[i,j])
                else:
                    self.update_gameboard()
        self.click_count += 1
    def update_gameboard(self,*args):
        if self.is_finished:
            return
        else:
            Clock.schedule_once(partial(self.eliminate_btns),.1)
            Clock.schedule_once(partial(self.drop_jewels),.2)
            Clock.schedule_once(partial(self.check_board),.2 + .06 * self.nrows)
            Clock.schedule_once(partial(self.update_gameboard),.3 + .06 * self.nrows)
    def eliminate_btns(self,*args):
        for btn in self.e_list:
            self.btn_matrix[btn[0]][btn[1]].background_color = [0,0,0,self.btn_alpha]
    def drop_jewels(self,*args):
        start_time = 0
        # while len(self.e_list) > 0:
        for i in range(self.num_drop_level()):
            Clock.schedule_once(partial(self.drop_one_level),start_time)
            #self.drop_one_level(dt)
            start_time += 0.06
        #pprint (self.e_list)
    def num_drop_level(self):
        num_level = 0
        current = self.e_list
        for btn in self.e_list:
            if btn[0] == current:
                continue
            else:
                current = btn[0]
                num_level += 1
        return num_level
    def drop_one_level(self,*args):
        self.sort_e_list()
        #pprint (self.e_list)

        if len(self.e_list) == 0:
            return
        current_level = self.e_list[0][0]
        while True:
            if len(self.e_list) > 0 and self.e_list[0][0] == current_level:
                btn = self.e_list.pop(0)
                for i in range(current_level):
                    self.btn_matrix[btn[0]-i][btn[1]].background_color = self.btn_matrix[btn[0]-i-1][btn[1]].background_color

                self.btn_matrix[0][btn[1]].background_color[:3] = self.color_dict[r(
                        0, len(self.color_dict)-1)][:3]
                self.btn_matrix[0][btn[1]].background_color[3] = self.btn_alpha
            else:
                break
    def check_board(self,*args):
        self.is_finished = True
        init_score = self.score
        for i in range(self.nrows):
            for j in range(self.ncols):
                if j+2 < self.ncols:
                    if self.btn_matrix[i][j].background_color[:3] == self.btn_matrix[i][j+1].background_color[:3]:
                        if self.btn_matrix[i][j].background_color[:3] == self.btn_matrix[i][j+2].background_color[:3]:
                            self.score += 3
                            for x in range(3):
                                self.btn_matrix[i][j+x].background_color[3] = 1
                                #add the jewels to remove to a list
                                self.e_list.append([i,j+x])
                if i+2 < self.nrows:
                    if self.btn_matrix[i][j].background_color[:3] == self.btn_matrix[i+1][j].background_color[:3]:
                        if self.btn_matrix[i][j].background_color[:3] == self.btn_matrix[i+2][j].background_color[:3]:
                            self.score += 3
                            for x in range(3):
                                self.btn_matrix[i+x][j].background_color[3] = 1
                                #add the jewels to remove to a list
                                self.e_list.append([i+x,j])
        self.sort_e_list()
        self.update_score()
        #Check if the move is successful
        if init_score == self.score:
            self.is_finished = True
        else:
            self.is_finished = False
    def update_score(self):
        self.play_label_score.text = 'Score: %d'%self.score

    def start_game(self, instance):
        self.clear_widgets()
        self.restart_set()
        self.size_window(self.nrows,self.ncols)
        # 1. initialize and load tht board
        self.load_board()
        if self.timer_is_on:
            return
        Clock.schedule_interval(self.time_cal, 0.1)  # x s刷新一次
        self.timer_is_on = True
    def time_cal(self, dt):
        self.time_passed += dt
        self.time_left -= dt
        self.play_label_time_passed.text = 'Time Passed: %.1f' % self.time_passed
        self.play_label_time_left.text = 'Time Left: %.1f' % self.time_left
        self.play_label_score.text = 'Score: %d'%self.score
        if self.time_left <= 0:
            self.clear_widgets()
            self.restart_set()
            self.size_window(self.nrows,self.ncols)
            # 1. initialize and load tht board
            self.load_board()
    def load_board(self):
        self.add_widget(self.play_label_title)
        self.add_widget(self.play_layout_btn)
        self.add_widget(self.play_layout_status)
        # add the gameboard to the main layout
        self.layout_gameboard = GridLayout(
            padding=10, spacing=10, cols=self.ncols, rows=self.nrows)
        self.add_widget(self.layout_gameboard)
        self.add_widget(self.play_lable_copyright)
        self.init_board()
    def init_board(self):
        # initialize a matrix to record all the buttons
        self.btn_matrix = [
            [0 for j in range(self.ncols)] for i in range(self.nrows)]
        # build buttons with random color from the dictionary
        for i in range(self.nrows):
            for j in range(self.ncols):
                # text = '({},{})'.format(i,j))
                self.btn_matrix[i][j] = Button(
                    on_press=partial(self.button_action, i, j))

                self.btn_matrix[i][j].background_normal = ''
                self.layout_gameboard.add_widget(self.btn_matrix[i][j])
                self.init_btn_color(i, j)
        return self.btn_matrix
    def init_btn_color(self, i, j):
        unused_bc = []
        for bc in self.color_dict:
            unused_bc.append(bc)
        if i >=2 and  self.btn_matrix[i - 1][j].background_color == self.btn_matrix[i - 2][j].background_color:
            unused_bc.remove(self.btn_matrix[i - 1][j].background_color)
        if j >= 2 and self.btn_matrix[i][j - 1].background_color == self.btn_matrix[i][j - 2].background_color:
            try:
                unused_bc.remove(self.btn_matrix[i][j -1].background_color)
            except:
                pass
        self.btn_matrix[i][j].background_color = unused_bc[r(
             0, len(unused_bc) - 1)]

    # size the window accoording to nrows and ncols
    def size_window(self,nrows,ncols):
        jewel_size = 40
        padding = 10
        x = (jewel_size + padding) * ncols + padding
        y = ((jewel_size + padding) * nrows + padding) + 125
        Window.size = (x, y)
        return [x,y]
    def sort_e_list(self):
        self.e_list = sorted(list(eval(x) for x in set([str(x) for x in self.e_list])))
    def switch_button(self,btn1,btn2,*args):
        temp_button_color = self.btn_matrix[btn1[0]][btn1[1]].background_color
        self.btn_matrix[btn1[0]][btn1[1]].background_color = self.btn_matrix[btn2[0]][btn2[1]].background_color
        self.btn_matrix[btn2[0]][btn2[1]].background_color = temp_button_color

    def restart_set(self):
        self.score, self.time_passed, self.time_left = [0, 0, 60]
        self.click_count = 0
    def return_to_menu(self, instance):
        self.clear_widgets()
        Window.size = (500, 600)
        self.add_widget(self.menu_layout_main)

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        # 定义一些控件
        self.e_list = []
        self.is_finished = True
        self.ncols, self.nrows, self.score, self.time_passed, self.time_left = [
                    10, 10, 0, 0, 60]
        self.click_count = 0
        self.timer_is_on = False
        self.ncolors = 6

        # possible colors of the Jewels in rgba coodinates
        self.color_bank = []
        self.btn_alpha = .55
        self.color_bank.append([1, 0.85, 0.73, self.btn_alpha])
        self.color_bank.append([0.59, 1, 1, self.btn_alpha])
        self.color_bank.append([1, 0.42, 0.42, self.btn_alpha])
        self.color_bank.append([1, 0.65, 0, self.btn_alpha])
        self.color_bank.append([0.85, 0.44, 0.84, self.btn_alpha])
        self.color_bank.append([0.68, 1, 0.18, self.btn_alpha])
        self.color_dict = self.color_bank[:self.ncolors]

        self.play_label_title = Label(
            text='Eliminates the Jewels', size_hint_y = None, height = 50, font_size='25sp')
        self.play_layout_btn = BoxLayout(
            orientation='horizontal', size_hint_y = None, height = 90, spacing=5, padding=5)
        self.play_btn_return = Button(text='Return to Menu',
                                      background_normal='', background_color=[0, 1, 0, .5], color=[0, 0, 0, .8])
        self.play_btn_return.bind(on_press=self.return_to_menu)
        self.play_btn_startover = Button(text='Start Over',
                                         background_normal='', background_color=[1, 0, 0, .5], color=[0, 0, 0, 1])
        self.play_btn_startover.bind(on_press=self.start_game)
        self.play_layout_btn.add_widget(self.play_btn_return)
        self.play_layout_btn.add_widget(self.play_btn_startover)
        # layout for the status section
        self.play_layout_status = BoxLayout(
            orientation='horizontal', size_hint_y = None, height = 40, spacing=10)
        #self.play_layout_status = StackLayout(
        self.play_label_score = Label(text='Score: %d'%self.score)
        self.play_label_time_passed = Label(
            text='Time Passed: %.1f' % self.time_passed)
        self.play_label_time_left = Label(
            text='Time Left: %.1f' % self.time_left)
        #self menu_input
        self.play_layout_status.add_widget(self.play_label_score)
        self.play_layout_status.add_widget(self.play_label_time_passed)
        self.play_layout_status.add_widget(self.play_label_time_left)
        self.play_lable_copyright = Label(
            text='Made by Changxuan Wu and Shuyang Deng in 2018',
            size_hint_y = None, height = 60)

        self.menu_layout_main = BoxLayout(orientation = "vertical")
        self.menu_picture = AsyncImage(source='back.png',size_hint= (2, 3),pos_hint={'center_x':.5, 'center_y':.5})
        self.menu_layout_btn = BoxLayout(orientation = "horizontal",padding = 10, spacing = 10,size_hint_y =None,height = 100)
        self.menu_btn_start = Button(text='Start')
        self.menu_btn_start.bind(on_press=self.start_game)
        self.menu_btn_option = Button(text = 'Options')
        self.menu_btn_option.bind(on_press=self.open_options)
        self.menu_layout_btn.add_widget(self.menu_btn_start)
        self.menu_layout_btn.add_widget(self.menu_btn_option)

        self.menu_layout_main.add_widget(self.menu_picture)
        self.menu_layout_main.add_widget(self.menu_layout_btn)
        self.add_widget(self.menu_layout_main)

        self.option_layout_main = BoxLayout(orientation = "vertical")

        self.option_layout_nrow = BoxLayout(orientation = "horizontal",size_hint_y=1,padding = 25,spacing = 20)
        self.option_ui_nrows = TextInput(text=str(self.nrows), size_hint_x = .5,multiline = False)
        self.option_layout_nrow.add_widget(Label(text = "Number of Rows"))
        self.option_layout_nrow.add_widget(self.option_ui_nrows)

        self.option_layout_ncol = BoxLayout(orientation = "horizontal",size_hint_y=1,padding = 25,spacing = 20)
        self.option_ui_ncols = TextInput(text=str(self.ncols), size_hint_x = .5,multiline = False)
        self.option_layout_ncol.add_widget(Label(text = "Number of Columns"))
        self.option_layout_ncol.add_widget(self.option_ui_ncols)

        self.option_layout_color = BoxLayout(orientation = "horizontal",size_hint_y=1,padding = 25,spacing = 20)
        self.option_ui_color = TextInput(text=str(self.ncolors), size_hint_x = .5,multiline = False)
        self.option_layout_color.add_widget(Label(text = "Number of Colors"))
        self.option_layout_color.add_widget(self.option_ui_color)

        self.option_layout_btn = BoxLayout(orientation = "horizontal",spacing = 15,padding = 15)
        self.option_btn_confirm = Button(text = "Confrim")
        self.option_layout_btn.add_widget(self.option_btn_confirm)
        self.option_btn_confirm.bind(on_press= self.confirm_change)
        self.option_btn_return  = Button(text = "Return")
        self.option_btn_return.bind(on_press=self.return_to_menu)
        self.option_layout_btn.add_widget(self.option_btn_return)

        self.option_layout_main.add_widget(Label(text = "Options", size_hint_y=1, font_size='25sp'))
        self.option_layout_main.add_widget(self.option_layout_nrow)
        self.option_layout_main.add_widget(self.option_layout_ncol)
        self.option_layout_main.add_widget(self.option_layout_color)
        self.option_layout_main.add_widget(self.option_layout_btn)



        self.sound = SoundLoader.load('bingo.mp3')
        self.bingo = SoundLoader.load('bingo.mp3')
        self.first_button = None
        self.second_button = None


class CandyCrushApp(App):
    def build(self):
        Config.set('graphics', 'width', '500')
        Config.set('graphics', 'height', '600')
        Config.write()
        # main layout of the game when user is playing
        root = MainLayout(orientation='vertical')
        return root


if __name__ == '__main__':
    CandyCrushApp().run()
