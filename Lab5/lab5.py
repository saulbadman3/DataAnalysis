import matplotlib.pyplot as plt
import scipy
import numpy as np
from matplotlib.widgets import Button, CheckButtons, Slider

sliders_config: list[tuple] = [("Frequency", "frequency",(1, 8)), 
                  ("Amplitude", "amplitude",(0.1, 5)), 
                  ("Phase", "phase",(0, 2*np.pi)), 
                  ("Noise Mean", "noise_mean",(-2.5, 2.5)), 
                  ("Noise Covariance", "noise_covariance", (0.1, 5)),
                  ("Cutoff frequency", "cutoff_freq", (1, 7)) 
    ]

class HarmonyPlot():
    def __init__(self: "HarmonyPlot", sliders_config: list[tuple]) -> None:
        self.initial_values: dict = {"amplitude":1, "frequency":2, "phase":np.pi, "noise_mean":0,
                         "noise_covariance":0.5, "cutoff_freq": 1}
        self.values: dict = self.initial_values.copy()
        self.sliders_config = sliders_config

        self.timeline: np.ndarray = np.linspace(0, 4 * np.pi, 1000)

        self.fig, self.ax = self.setup_plot()
        
        self.sliders: dict[str, Slider] = {}
        self.checkbox: CheckButtons = None
        self.harmony, self.noise, self.harmony_line, \
            self.noise_line, self.filtered_line = [None] * 5
        self.setup_controls()

    # Method to setup the plot
    def setup_plot(self: "HarmonyPlot") -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(15, 10))
        plt.subplots_adjust(left=0.1, right=0.85, bottom=0.4, top=0.96)
        ax.set_title("Sinus-harmony function with noise", fontweight='bold')
        ax.set_xticks(np.arange(0, 4*np.pi, np.pi))
        ax.set_xticklabels(['0', 'π', '2π', '3π'])
        ax.set_xlim(0, 4*np.pi)
        ax.grid(True)
        return fig, ax

    # Method to draw checkboxes, button, sliders and plots
    def setup_controls(self: "HarmonyPlot") -> None:
        self.calculate_harmony()
        self.calculate_noise()
        for i, (label, key, val_range) in enumerate(self.sliders_config):
            slider = Slider(plt.axes([0.1, 0.3 - i * 0.05, 0.6, 0.03]),
                             label, val_range[0], val_range[1], valinit=self.initial_values[key])
            slider.on_changed(lambda val, k=key: self.update_value(k, val))
            self.sliders[key] = slider
        
        reset_btn = Button(plt.axes([0.75, 0.1, 0.12, 0.05]), 'Reset', color="lightblue")
        reset_btn.on_clicked(self.reset)

        self.checkbox = CheckButtons(plt.axes([0.75, 0.18, 0.12, 0.08]), ['Show harmony', 'Show noise', 'Show filtered'], [True, True, False])
        self.checkbox.on_clicked(self.checkbox_status)
        
        self.noise_line, = self.ax.plot(self.timeline, self.harmony+self.noise, label='Noise')
        self.harmony_line, = self.ax.plot(self.timeline, self.harmony, label='Clean')
        self.filtered_line, = self.ax.plot(self.timeline, self.calculate_filtered_harmony(), label='Filtered')
        self.filtered_line.set_visible(False)
        self.ax.legend()
        plt.show()

    # Method to calculate harmony array
    def calculate_harmony(self: "HarmonyPlot") -> None:
        self.harmony: np.ndarray = self.values['amplitude'] \
            * np.sin(self.values['frequency'] * self.timeline + self.values['phase'])
    
    # Method to calculate noise array
    def calculate_noise(self: "HarmonyPlot") -> None:
        self.noise: np.ndarray = np.random.normal(self.values['noise_mean'], np.sqrt(self.values['noise_covariance']), len(self.timeline))
    
    # Method to calculate filtered harmony
    def calculate_filtered_harmony(self: "HarmonyPlot") -> np.ndarray:
        b, a = scipy.signal.butter(5, self.values["cutoff_freq"] / (0.5 * 1000/(4*np.pi)), btype='low')
        return scipy.signal.filtfilt(b, a, self.harmony+self.noise)
    
    # Method to update values dict when sliders are moved and recalculate the corresponding array
    def update_value(self: "HarmonyPlot", key: str, val: float) -> None:
        self.values[key] = val
        match key:
            case "amplitude" | "frequency" | "phase":
                self.calculate_harmony()
            case "noise_mean" | "noise_covariance":
                self.calculate_noise()
        self.update_plots()

    # Method to update the plots based on changed values
    def update_plots(self: "HarmonyPlot") -> None:
        self.harmony_line.set_ydata(self.harmony)
        self.noise_line.set_ydata(self.harmony+self.noise)
        self.filtered_line.set_ydata(self.calculate_filtered_harmony())
        if any(self.checkbox.get_status()):
            self.fig.canvas.draw_idle()  

    # Method to react on checbox press to redraw the plots
    def checkbox_status(self: "HarmonyPlot", event=None) -> None:
        self.harmony_line.set_visible(self.checkbox.get_status()[0])
        self.noise_line.set_visible(self.checkbox.get_status()[1])
        self.filtered_line.set_visible(self.checkbox.get_status()[2])
        self.fig.canvas.draw_idle()
        self.ax.legend()

    # Method for the reset button
    def reset(self: "HarmonyPlot", event=None) -> None:
        self.checkbox.set_active(0, True)
        self.checkbox.set_active(1, True)
        self.checkbox.set_active(2, False)
        for _, slider in self.sliders.items():
            slider.reset()

def main() -> None:
    HarmonyPlot(sliders_config)

if __name__ == "__main__":
    main()