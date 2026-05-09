import ipywidgets as widgets
from IPython.display import display
import time

status_banner = widgets.HTML(
    value="",
    layout=widgets.Layout(width='100%', height='180px')
)

# display(status_banner)
def show_plan(content, times=8, delay=0.2):
    sizes = [80, 100, 110, 95]

    for i in range(times):
        size = sizes[i % len(sizes)]
        status_banner.value = f"""
        <div style='text-align:center;
                    font-weight:900;
                    color:lime;
                    background-color:black;
                    padding:30px;
                    border-radius:15px;
                    line-height:1.6;'>

            <div style="font-size:{int(size*0.8)}px;">{content}</div>

        </div>
        """
        time.sleep(delay)

def show_success(times=8, delay=0.2):
    sizes = [80, 100, 110, 95]

    for i in range(times):
        size = sizes[i % len(sizes)]
        status_banner.value = f"""
        <div style='text-align:center;
                    font-weight:900;
                    color:lime;
                    background-color:black;
                    padding:30px;
                    border-radius:15px;
                    line-height:1.6;'>

            <div style="font-size:{int(size*0.8)}px;">🎯 FOUND IT!</div>
            <div style="font-size:{size}px; margin-top:30px;">FOUND</div>

        </div>
        """
        time.sleep(delay)


def show_failure(times=8, delay=0.25):
    colors = ["red", "orange", "white"]

    for i in range(times):
        color = colors[i % len(colors)]
        status_banner.value = f"""
        <div style='text-align:center;
                    font-weight:900;
                    color:{color};
                    background-color:black;
                    padding:30px;
                    border-radius:15px;
                    line-height:1.6;'>

            <div style="font-size:70px;">❌ NOPE! </div>
            <div style="font-size:90px; margin-top:30px;">NOT FOUND</div>

        </div>
        """
        time.sleep(delay)
