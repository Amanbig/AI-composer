
import matplotlib.pyplot as plt
import numpy as np

def plot_waveform(audio_data, sample_rate):
    """
    Generates a matplotlib figure of the waveform.
    """
    # Create time axis
    time = np.linspace(0, len(audio_data) / sample_rate, num=len(audio_data))
    
    # Setup dark theme plot
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot data
    # Downsample for performance if needed, but for short clips it's fine
    ax.plot(time, audio_data, color='#00d4ff', alpha=0.8, linewidth=0.5)
    
    # Styling
    ax.set_title("Audio Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    
    # Dark background styling
    ax.set_facecolor('#0E1117')
    fig.patch.set_facecolor('#0E1117')
    
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white') 
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.tick_params(axis='x', colors='#FAFAFA')
    ax.tick_params(axis='y', colors='#FAFAFA')
    ax.yaxis.label.set_color('#FAFAFA')
    ax.xaxis.label.set_color('#FAFAFA')
    ax.title.set_color('#FAFAFA')
    
    plt.tight_layout()
    return fig
