import XBee
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import sys

fig, ax = plt.subplots()

data = []
gps_data = ''
packages = 0

# some X and Y data
text_x = 300
text_y = 230
upper_bound = 1100.0
lower_bound = 200.0
num_pixels = 2048
x = []

for i in np.linspace(lower_bound, upper_bound, num_pixels, endpoint=False):
    x.append(i)

y = [0] * num_pixels
ax.set_ylim([-5, 250])
line, = ax.plot(x, y)
gps_text = ax.text(text_x, text_y, '')


def animate(loop):
    global packages, data, gps_data
    message = xbee.receive()
    if message:
        print('Found message')
        if packages == 0:
            # Get GPS DATA
            temp_message = message[14:-1]
            if len(temp_message) < 256:
                gps_data = temp_message.decode('ascii')
                print(gps_data)
                packages += 1
        else:
            temp_message = message[14:-1]
            if len(temp_message) == 256:
                data.extend(temp_message)
                packages += 1
            else:
                gps_data = temp_message.decode('ascii')
                packages = 1
                data = []

    if packages >= 9:
        packages = 0
        print('First: {0}, Last: {1}, Length: {2}'.format(data[0], data[-1], len(data)))
        if len(data) == num_pixels:
            line.set_ydata(list(map(int, data)))  # update the data
        data = []
        gps_text.set_text(gps_data)

    return gps_text, line


# Init only required for blitting to give a clean slate.
def init():
    line.set_ydata(np.ma.array(x, mask=True))
    return line,


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python xbee_main.py <serial-port>")
        sys.exit(0)

    port = sys.argv[1]
    print("Connecting to port", port)
    xbee = XBee.XBee(port)  # Your serial port name here

    # Begin animation
    ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
                                  interval=10, blit=True)
    plt.show()
