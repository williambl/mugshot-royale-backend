class Game:

    def __init__(self, lat, long, rad, freq, socketio):
        self.lat = lat
        self.long = long
        self.rad = rad
        self.freq = freq
        self.socketio = socketio

    def shrink_safe_zone():
        wait_time = freq/i
        new_radius = rad/(i+1)

        socketio.emit("safe-zone-will-shrink", {"rad": new_radius, "lat": lat, "long": long, "time": wait_time}, namespace="/websocket", broadcast=True)

        await asyncio.sleep(wait_time)
        rad = new_radius
        print("radius: " + str(rad) + ", shrink frequency: "+ str(freq))

