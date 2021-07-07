import random
from tkinter.constants import BOTTOM, RIGHT, TOP, LEFT
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import BooleanVar, DoubleVar, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from assets import *
from matplotlib.figure import Figure
import matplotlib.animation as animation

def init(percentage, L):
    """Initialize net.

    Args:
        percentage (float): the ratio of the number of people with a positive opinion to everyone,
        L (int): net size.
    Returns:
        [numpy array]: net with a structured opinion.
    """
    N = L**2
    p = percentage*N
    voters = np.random.permutation([1]*round(p) + [-1]*(N - round(p)))
    return voters.reshape((L, L))

def qVoter_model(initialization, opinion, L, q, p, replace, independence=False, anticonformity=False, f=0):
    """Generate q-voter model for one Monte Carlo step.

    Args:
        initialization (numpy array): init net,
        opinion (array): list of average opinions for MC steps,
        L (int): net size,
        q (int): influence group size,
        p (float): probability of nonconformity,
        replace (bool): draw neighbors with repeating (when True) and without repeating (when False),
        independence (bool, optional): if independence is chosen. Defaults to False.
        anticonformity (bool, optional): if anticonformity is chosen. Defaults to False.
        f (float, optional): probability of change opinion when independence.

    Returns:
        [list of arrays]: voters net, avaerage opinion array.
    """
    N = L**2
    voters = initialization
     
    plus_opinion = np.count_nonzero(voters == 1) #liczymy wyborców z opinią 1
    opinion_value = (plus_opinion + (-1)*(N-plus_opinion))/N
    opinion.append(opinion_value) #średnia opinia w czasie
    
    for __ in range(N):
        #losujemy wyborcę
        x, y = random.randint(-1, L-2), random.randint(-1, L-2)
        neighbours = [[x-1, y], [x+1, y], [x, y-1], [x, y+1]]

        #grupa wpływów = tablica współrzędnych sąsiadów, ich ilość to q, replace odpowiada za powtarzanie losowania sąsiadów 
        #brzegi
        group_of_influence = [neighbours[m] for m in np.random.choice([0,1,2,3], q, replace=replace)] 

        U = random.random() #losujemy zmienną z przedziału (0, 1)
        #jeżeli zmienna jest większa niż prawdopodobieństwo nonkonformizmu, to robimy konformizm
        if U > p:
            #sumujemy wszystkie opinie sąsiadów i jeżeli grupa jest zgodna, to zmieniamy opinię na opinię grupy
            if abs(sum([voters[group_of_influence[i][0], group_of_influence[i][1]] for i in range(q)])) == q:
                    voters[x, y] = voters[group_of_influence[0][0], group_of_influence[0][1]]

        #w przeciwnym wypadku robimy nonkonformizm
        else:
            if independence == True:
                U2 = random.random()
                #f - prawdopodobieństwo z jakim zmieniamy opinię
                if U2 < f:
                    voters[x, y] *= -1
            #antykonfomizm - jeżeli grupa jest zgodna, to zmieniamy opinię na przeciwną, niż grupa
            elif anticonformity == True:
                if abs(sum([voters[group_of_influence[i][0], group_of_influence[i][1]] for i in range(q)])) == q:
                    voters[x, y] = (-1)*voters[group_of_influence[0][0], group_of_influence[0][1]]
    return voters, opinion #zwracamy siatkę po jednym kroku, średnią opinię po czasie


class Application(tk.Frame):
    """Create q-voter model application."""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Model Q-wyborcy")
        
        self.master.geometry('950x650')
        self.master.configure(background=background_color)
        self.pack()
        
        self.stop = False
        self.created_labels_and_entry_fields()
        self.created_draw_btn()
        self.created_stop_btn()
        self.created_button_quit()
        self.created_continue_btn()
        figure = Figure(figsize=(3.5, 3.5), facecolor=background_color)
        self.fig = figure
        self.ax1 = figure.subplots()
        self.ax1.axis("off")

    def created_labels_and_entry_fields(self):
        """Create application window elements."""
        self.size = tk.Label(self.master, text="Rozmiar układu", background=background_color, font=label_font, justify='center')
        self.size.pack(side=TOP)
        self.size.place(x=25, y=5)
        
        self.L = tk.IntVar()
        self.entry_size = tk.Entry(self.master, width=26, textvariable=self.L, font=label_font, justify='center', border=False)
        self.entry_size.pack(side=BOTTOM)
        self.entry_size.place(x=25, y=32)

        self.influence_size = tk.Label(self.master, text="Rozmiar grupy wpływu", background=background_color, font=label_font, justify='center')
        self.influence_size.pack(side=TOP)
        self.influence_size.place(x=25, y=67)

        self.q = tk.IntVar()
        self.entry_influence = ttk.Combobox(self.master, width=21, textvariable=self.q)
        self.entry_influence['value'] = (1, 2, 3, 4)
        self.entry_influence.current(0)
        self.entry_influence.pack(side=BOTTOM)
        self.entry_influence.place(x=25, y=90)
    
        self.check_value = BooleanVar()
        self.check_repeatment = tk.Checkbutton(self.master, text="Powtarzanie losowania sąsiadów", font=label_font, variable = self.check_value, onvalue = True, offvalue = False, background=background_color)
        self.check_repeatment.pack()
        self.check_repeatment.place(x=25, y=115)

        self.init_positve_opinion = tk.Label(self.master, text="Początkowe zagęszczenie pozytywnej opini", font=label_font, background=background_color)
        self.init_positve_opinion.pack()
        self.init_positve_opinion.place(x=25, y=155)

        self.positive_opinion = DoubleVar()
        self.positive_opinion_slider = tk.Scale(self.master, from_ = 0.0, to = 1.0,
                                                orient='horizontal', resolution=0.1, variable=self.positive_opinion, length=200)
        self.positive_opinion_slider.pack()
        self.positive_opinion_slider.place(x=25, y=179)

        self.nonkonfonism_prob = tk.Label(self.master, text="Prawdopodobieństwo nonkonformizu", font=label_font, background=background_color)
        self.nonkonfonism_prob.pack()
        self.nonkonfonism_prob.place(x=25, y=232)

        self.nonkonf_prob = DoubleVar()
        self.nonkonf_prob_slider = tk.Scale(self.master, from_ = 0.0, to = 1.0,
                                                orient='horizontal', resolution=0.1, variable=self.nonkonf_prob, length=200)
        self.nonkonf_prob_slider.pack()
        self.nonkonf_prob_slider.place(x=25, y=256)

        self.nonkonfornism_type= tk.Label(self.master, text="Typ nonkonformizu", font=label_font, background=background_color)
        self.nonkonfornism_type.pack()
        self.nonkonfornism_type.place(x=25, y=305)
        
        self.anticonformity = BooleanVar()
        self.check_antykonf = tk.Radiobutton(self.master, text="antykonformizm",font=radiobutton_font, variable=self.anticonformity, value=True, background=background_color)
        self.check_antykonf.select()
        self.check_antykonf.pack(side=LEFT)
        self.check_antykonf.place(x=25, y=327)

        self.check_independence = tk.Radiobutton(self.master, text="niezależność", font=radiobutton_font, variable=self.anticonformity, value=False, background=background_color)
        self.check_independence.select()
        self.check_independence.pack(side=RIGHT)
        self.check_independence.place(x=150, y=327)

        self.independence_prob = tk.Label(self.master, text="Prawdopodobieństwo zmiany opini przy niezależności",font=label_font, background=background_color)
        self.independence_prob.pack()
        self.independence_prob.place(x=25, y=360)

        self.f= DoubleVar()
        self.indepen_prob_slider = tk.Scale(self.master, from_ = 0.0, to = 1.0,
                                                orient='horizontal', resolution=0.1, variable=self.f, length=200)
        self.indepen_prob_slider.pack()
        self.indepen_prob_slider.place(x=25, y=384)

        self.frame = tk.Frame(self.master)
        self.frame.place(x=360, y=0)

    def animate(self, fig):
        """Generate animation."""

        for widget in self.frame.winfo_children():
            widget.destroy()
        self.independence = not(self.anticonformity.get())
        anim = AnimationModel(fig, self.nonkonf_prob.get(), self.positive_opinion.get(), self.check_value.get(), self.L.get(),
        self.f.get(), self.q.get(), self.independence, self.anticonformity.get())
        return anim

    def animation_display(self):
        """Display animation."""

        fig = Figure(facecolor=background_color)
        self.anim = self.animate(fig)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.get_tk_widget().pack()
        self.anim.simulation_show()

    def pause(self):
        """Pause animation."""

        self.anim.anim.event_source.stop()

    def continue_anim(self):
        """Start animation after pause."""

        self.anim.anim.event_source.start()

    def created_draw_btn(self):
        """Create button to start animation."""

        self.draw_btn = tk.Button(self.master, text="START", font=('Roboto', 12, 'bold'), foreground=button_text_color, relief="ridge", activebackground=light_green, background=green, 
        command=self.animation_display)
        self.draw_btn.pack()
        self.draw_btn.place(x=25, y=450)

    def created_stop_btn(self):
        """"Create button to stop animation."""

        self.stop_btn = tk.Button(self.master, text="STOP", font=('Roboto', 12, 'bold'), foreground=button_text_color, activebackground=light_red, background=red, relief="ridge",  command=self.pause)
        self.stop_btn.pack()
        self.stop_btn.place(x=115, y=450)

    def created_continue_btn(self):
        """Create button to continue animation."""
        self.continue_btn = tk.Button(self.master, text="WZNÓW", font=('Roboto', 12, 'bold'), foreground=button_text_color, relief="ridge", activebackground=light_orange, background=orange, command=self.continue_anim)
        self.continue_btn.pack()
        self.continue_btn.place(x=180, y=450)

    def created_button_quit(self):
        self.quit_btn = tk.Button(self.master, command=self.master.quit, text="ZAKOŃCZ", font=('Roboto', 12, 'bold'), foreground=button_text_color, relief="ridge", activebackground=light_blue, background=dark_blue)
        self.quit_btn.pack()
        self.quit_btn.place(x=25, y=500)
    
class AnimationModel:
    """Create q-voter model animation."""
    def __init__(self, fig, p, percentege, replace, L, f, q, independence, anticonformity):
        self.fig = fig
        self.p = p
        self.percentege = percentege
        self.replace = replace
        self.L = L
        self.q = q
        self.f = f
        self.independence = independence
        self.anticonformity = anticonformity
        self.time = 0
        self.opinion = []
        self.cmap = matplotlib.colors.ListedColormap([cmap_min_color, cmap_max_color])  
        self.time_range = [0]
        self.initial_plot_set_up()

    def initial_plot_set_up(self):
        """Set initial plot parameters."""
        self.fig.set_figheight(6)
        self.fig.set_figwidth(6)
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.axis("off")
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_ylim(-1.01, 1.01)
        self.ax2.set_title("Średnia opinia zmieniająca się w czasie")
        self.ax2.set_ylabel("średnia opinia")

    def animate_func(self, j):
        """Create animation."""
        #sprawdzamy czy to początek symulacji
        if self.time == 0:
            #inicjalizacja warunków początkowych
            #self.opinion = []
            self.initialization = init(self.percentege, self.L)
     
            self.plus_opinion = np.count_nonzero(self.initialization == 1) #liczymy wyborców z opinią 1
            self.opinion.append((self.plus_opinion + (-1)*((self.L**2)-self.plus_opinion))/(self.L**2))

            self.heat_map = self.ax1.imshow(self.initialization, vmin=-1, vmax=1, cmap=self.cmap)
            self.opinion_plot, = self.ax2.plot(self.time_range, self.opinion, color="purple")
        else:
            self.initialization, self.opinion = qVoter_model(self.initialization, self.opinion, self.L, self.q, self.p, self.replace, independence=self.independence,  anticonformity=self.anticonformity, f=self.f)
        #ustawienia heatmapy
        self.ax1.set_title("{time} [MCS]".format(time=self.time))
        self.heat_map.set_array(np.copy(self.initialization)) #aktualizacja heatmapy

        #ustawienia wykresu opini
        self.ax2.set_xlabel("time [MCS]")
        self.ax2.set_xlim(0, self.time)
        self.opinion_plot.set_data(np.array(self.time_range), np.array(self.opinion))

        self.time += 1
        self.time_range.append(self.time) #zakres czasu
        return [self.heat_map], self.opinion_plot,

    def simulation_show(self):
        """Show animation"""
        
        self.anim = animation.FuncAnimation(
                                    self.fig, 
                                    self.animate_func, 
                                    interval = 5,
                                    repeat = False,
                                    )
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()