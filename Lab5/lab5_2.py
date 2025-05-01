from bokeh.io import curdoc
from bokeh.document import Document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup, Button
from bokeh.plotting import figure
import numpy as np
import scipy.signal

class HarmonyPlotBokeh:
    def __init__(self: "HarmonyPlotBokeh", doc: Document):
        self.initial_values = {
            "amplitude": 1, "frequency": 2, "phase": np.pi,
            "noise_mean": 0, "noise_covariance": 0.5,
            "cutoff_freq": 1
        }
        self.values = self.initial_values.copy()
        self.timeline = np.linspace(0, 4 * np.pi, 1000)


        self.noise = self.calculate_noise()
        self.harmony = self.calculate_harmony()
        self.source = ColumnDataSource(data=dict(x=self.timeline, clean=[], noisy=[], filtered=[]))

        self.plot = figure(title="Sinus-harmony function with noise",
                           x_axis_label="Time", y_axis_label="Amplitude", width=900, height=400)
        self.line_clean = self.plot.line('x', 'clean', source=self.source, line_color="blue", legend_label="Clean")
        self.line_noisy = self.plot.line('x', 'noisy', source=self.source, line_color="red", legend_label="Noise")
        self.line_filtered = self.plot.line('x', 'filtered', source=self.source, line_color="green", legend_label="Filtered")
        self.line_filtered.visible = False

        self.create_widgets()
        self.update_data()

        layout = column(self.plot, self.sliders_layout, self.checkbox, self.reset_btn, self.regenerate_noise_btn)
        doc.add_root(layout)
        doc.title = "Harmony Plot"

    # Method to draw checkboxes, button, sliders and plots
    def create_widgets(self: "HarmonyPlotBokeh") -> None:
        self.sliders = {
            key: Slider(start=range[0], end=range[1], value=self.initial_values[key], step=0.01, title=label)
            for label, key, range in [
                ("Frequency", "frequency", (1, 8)),
                ("Amplitude", "amplitude", (0.1, 5)),
                ("Phase", "phase", (0, 2 * np.pi)),
                ("Noise Mean", "noise_mean", (-2.5, 2.5)),
                ("Noise Covariance", "noise_covariance", (0.1, 5)),
                ("Cutoff Frequency", "cutoff_freq", (1, 7)),
            ]
        }

        for key, slider in self.sliders.items():
            slider.on_change('value', lambda attr, old, new, k=key: self.on_slider_change(k, new))

        self.sliders_layout = column(*self.sliders.values())

        self.checkbox = CheckboxGroup(labels=["Show harmony", "Show noise", "Show filtered"], active=[0, 1])
        self.checkbox.on_change("active", lambda attr, old, new: self.update_visibility())

        self.reset_btn = Button(label="Reset", button_type="primary")
        self.reset_btn.on_click(self.reset)

        self.regenerate_noise_btn = Button(label="Regenerate Noise", button_type="success")
        self.regenerate_noise_btn.on_click(self.regenerate_noise)

    # Method to update values dict when sliders are moved and recalculate the corresponding array
    def on_slider_change(self: "HarmonyPlotBokeh", key, val) -> None:
        self.values[key] = val
        if key in ["amplitude", "frequency", "phase"]:
            self.harmony = self.calculate_harmony()
        elif key in ["noise_mean", "noise_covariance"]:
            self.noise = self.calculate_noise()
        self.update_data()

    # Method to calculate harmony array
    def calculate_harmony(self: "HarmonyPlotBokeh") -> np.ndarray:
        return self.values['amplitude'] * np.sin(self.values['frequency'] * self.timeline + self.values['phase'])

    # Method to calculate noise array
    def calculate_noise(self: "HarmonyPlotBokeh") -> np.ndarray:
        return np.random.normal(self.values['noise_mean'], np.sqrt(self.values['noise_covariance']), len(self.timeline))

    # Method to calculate filtered harmony
    def calculate_filtered(self: "HarmonyPlotBokeh", signal) -> np.ndarray:
        b, a = scipy.signal.butter(5, self.values["cutoff_freq"] / (0.5 * 1000 / (4 * np.pi)), btype='low')
        return scipy.signal.filtfilt(b, a, signal)

    # Method to update the plots based on changed values
    def update_data(self: "HarmonyPlotBokeh") -> None:
        noisy_signal = self.harmony + self.noise
        filtered = self.calculate_filtered(noisy_signal)
        self.source.data = dict(x=self.timeline, clean=self.harmony, noisy=noisy_signal, filtered=filtered)

    # Method to regenerate noise plot and update plot
    def regenerate_noise(self: "HarmonyPlotBokeh") -> None:
        self.noise = self.calculate_noise()
        self.update_data()

    # Method to react on checbox press to redraw the plots
    def update_visibility(self: "HarmonyPlotBokeh") -> None:
        self.line_clean.visible = 0 in self.checkbox.active
        self.line_noisy.visible = 1 in self.checkbox.active
        self.line_filtered.visible = 2 in self.checkbox.active

    # Method for the reset button
    def reset(self: "HarmonyPlotBokeh") -> None:
        for key, val in self.initial_values.items():
            self.sliders[key].value = val
        self.checkbox.active = [0, 1]
        self.harmony = self.calculate_harmony()
        self.noise = self.calculate_noise()
        self.update_data()
        self.update_visibility()

def main() -> None:
    HarmonyPlotBokeh(curdoc())

main()