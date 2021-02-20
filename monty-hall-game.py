from contextlib import suppress
import random
from tkinter import (
    BooleanVar, Button, Checkbutton, Frame, IntVar, Label, Spinbox, Tk)


CONFIG = {
    'title': 'Monty Hall game',
    'window_size': {
        'width': 450,
        'height': 240,
    },
    'font': {
        'XL': ('Consolas', '40', 'bold'),
        'L': ('Consolas', '28', 'bold'),
        'M': ('Consolas', '18', 'bold'),
        'S': ('Consolas', '16', 'bold'),
        'XS': ('Consolas', '14'),
    },
    'defaults': {
        'rounds': 20,
        'boxes': 3,
        'tips': True,
    },
    'colors': {
        'menu': 'grey',
        'score': 'white',
        'surface': '',
        'button_text': 'white',
        'button_active_text': 'black',
        'button_closed': 'black',
        'button_active': '#ffddaa',
        'button_win': '#bed6be',
        'button_fail': 'red',
        'button_empty': 'systembuttonface',
    },
}


class MontyHallModel:

    def __init__(self) -> None:
        self.boxes = []
        self.boxes_amount = None
        self.round = 0
        self.wins = 0
        self.fails = 0
        self.choice = None

    def start_game(self, boxes_amount: int) -> None:
        self.boxes_amount = boxes_amount
        self.round = 0
        self.wins = 0
        self.fails = 0

    def get_distribution(self) -> None:
        self.choice = None
        self.round += 1
        self.boxes = [False] * self.boxes_amount
        self.boxes[random.randint(0, self.boxes_amount - 1)] = True

    def made_choice(self, choice: int) -> None:
        self.choice = choice
        if self.boxes[self.choice]:
            self.wins += 1
        else:
            self.fails += 1

    def get_tips(self, choice: int) -> list[int]:
        boxes_to_open = list(range(len(self.boxes)))
        boxes_to_open.remove(choice)
        right_answer = self.boxes.index(True)
        if choice == right_answer:
            boxes_to_open.remove(random.choice(boxes_to_open))
        else:
            boxes_to_open.remove(right_answer)
        return boxes_to_open


class MontyHallController:

    def __init__(self, model: MontyHallModel) -> None:
        self._model = model
        self._view = None
        self._with_tips = True
        self._rounds_amount = None
        self._is_final_guess = True
        self._after_id = None

    def set_view(self, view: 'MontyHallInterface') -> None:
        self._view = view

    def start(self) -> None:
        if self._after_id:
            self._view.after_cancel(self._after_id)
        self._with_tips, boxes_amount, self._rounds_amount = \
            self._view.get_settings()
        self._model.start_game(boxes_amount)
        self._new_round()

    def _new_round(self) -> None:
        self._is_final_guess = True
        self._model.get_distribution()
        self._view.refresh_score()
        self._view.draw_buttons()

    def choose(self, chosen_box: int) -> None:
        if self._with_tips:
            self._is_final_guess = not self._is_final_guess
        if self._is_final_guess:
            self._model.made_choice(chosen_box)
            self._view.refresh_score()
            self._view.open_boxes(list(range(len(self._model.boxes))))
            if self._model.round < self._rounds_amount:
                self._after_id = self._view.after(5000, self._new_round)
            else:
                self._view.stop_game()
        else:
            boxes_to_open = self._model.get_tips(chosen_box)
            self._view.open_boxes(boxes_to_open)


class MontyHallInterface(Frame):

    def __init__(
            self, master: Tk, model: MontyHallModel,
            controller: MontyHallController) -> None:

        super().__init__(master)
        self.pack(fill='both', expand=True)
        self._master = master
        self._model = model
        self._controller = controller
        self._controller.set_view(self)
        self._buttons = []
        # widgets
        self._result_lab = None
        self._score_lab = None
        self._frame_boxes_child = None
        self._mode_var = BooleanVar()
        self._mode_var.set(CONFIG['defaults']['tips'])
        self._boxes_count_var = IntVar()
        self._boxes_count_var.set(CONFIG['defaults']['boxes'])
        self._rounds_count_var = IntVar()
        self._rounds_count_var.set(CONFIG['defaults']['rounds'])
        self._create_widgets()

    def _create_widgets(self) -> None:
        # settings
        settings_frame_parent = Frame(self, bg=CONFIG['colors']['menu'])
        settings_frame_child = Frame(
            settings_frame_parent, bg=CONFIG['colors']['menu'])
        tips_lab = Label(
            settings_frame_child,
            text='Tips:', bg=CONFIG['colors']['menu'],
            font=CONFIG['font']['XS'])
        mode_check = Checkbutton(
            settings_frame_child,
            variable=self._mode_var, font=CONFIG['font']['XS'],
            bg=CONFIG['colors']['menu'])
        rounds_count_lab = Label(
            settings_frame_child,
            text='Rounds:', bg=CONFIG['colors']['menu'],
            font=CONFIG['font']['XS'])
        rounds_count_spinbox = Spinbox(
            settings_frame_child,
            from_=1, to=100, width=3, textvariable=self._rounds_count_var,
            font=CONFIG['font']['M'])
        boxes_count_lab = Label(
            settings_frame_child,
            text='Boxes:', bg=CONFIG['colors']['menu'],
            font=CONFIG['font']['XS'])
        boxes_count_spinbox = Spinbox(
            settings_frame_child,
            from_=3, to=10, width=3, textvariable=self._boxes_count_var,
            font=CONFIG['font']['M'])
        start_but = Button(
            settings_frame_child,
            text='START', command=self._controller.start,
            font=CONFIG['font']['S'])
        # guess boxes
        score_frame = Frame(self)
        self._score_lab = Label(
            score_frame,
            bg=CONFIG['colors']['score'],
            text='Round: 00 | Wins: 00 | Fails: 00',
            font=CONFIG['font']['M'])
        # boxes
        frame_boxes_parent = Frame(self)
        self._frame_boxes_child = Frame(frame_boxes_parent)
        # PACKED
        settings_frame_parent.pack(fill='x')
        settings_frame_child.pack(expand=True, padx=5, pady=5)
        tips_lab.pack(side='left')
        mode_check.pack(side='left')
        rounds_count_lab.pack(side='left')
        rounds_count_spinbox.pack(side='left', fill='y')
        boxes_count_lab.pack(side='left')
        boxes_count_spinbox.pack(side='left', fill='y')
        start_but.pack(side='left', fill='y', padx=5)
        score_frame.pack(fill='x')
        self._score_lab.pack(fill='x')
        frame_boxes_parent.pack(fill='both', expand=True)
        self._frame_boxes_child.pack(expand=True, padx=20, pady=20)

    def draw_buttons(self) -> None:
        with suppress(AttributeError):
            self._result_lab.destroy()

        while self._buttons:
            button = self._buttons.pop()
            button.destroy()
        for i in range(self._model.boxes_amount):
            self._buttons.append(
                Button(
                    self._frame_boxes_child,
                    text=str(i + 1), width=3, bd=5,
                    command=lambda choice=i: self._controller.choose(choice),
                    bg=CONFIG['colors']['button_closed'],
                    fg=CONFIG['colors']['button_text'],
                    activebackground=CONFIG['colors']['button_active'],
                    activeforeground=CONFIG['colors']['button_text'],
                    font=CONFIG['font']['L']))
            self._buttons[i].pack(side='left', padx=10)

        master_width = CONFIG['window_size']['width']
        if self._model.boxes_amount > 4:
            master_width = CONFIG['window_size']['width'] \
                + (self._model.boxes_amount - 4) * 100

        self._master.geometry(
            f"{master_width}x{CONFIG['window_size']['height']}")
        self._master.minsize(
            width=master_width,
            height=CONFIG['window_size']['height'])

    def get_settings(self) -> tuple[bool, int, int]:
        return (
            self._mode_var.get(),
            self._boxes_count_var.get(),
            self._rounds_count_var.get(),
        )

    def open_boxes(self, boxes_to_open: list[int]) -> None:
        for box_num in boxes_to_open:
            if self._model.boxes[box_num]:
                color = CONFIG['colors']['button_win']
            elif box_num == self._model.choice:
                color = CONFIG['colors']['button_fail']
            else:
                color = CONFIG['colors']['button_empty']

            self._buttons[box_num].config(
                text='$' if self._model.boxes[box_num] else '',
                state='disabled', bg=color, relief='sunken',
                disabledforeground=CONFIG['colors']['button_active_text'])

    def refresh_score(self) -> None:
        self._score_lab.config(text=(
            f'Round: {self._model.round:2} | '
            f'Wins: {self._model.wins:2} | '
            f'Fails: {self._model.fails:2}'))

    def stop_game(self) -> None:
        while self._buttons:
            button = self._buttons.pop()
            button.destroy()

        result = round(self._model.wins / self._model.round * 100)
        self._result_lab = Label(
            self._frame_boxes_child,
            text=f'{result}% of wins!',
            font=CONFIG['font']['XL'])
        self._result_lab.pack()


def main() -> None:
    root = Tk()
    root.title(CONFIG['title'])
    root.minsize(**CONFIG['window_size'])

    mh_model = MontyHallModel()
    mh_controller = MontyHallController(mh_model)
    mh_view = MontyHallInterface(root, mh_model, mh_controller)

    mh_view.mainloop()


if __name__ == '__main__':
    main()
