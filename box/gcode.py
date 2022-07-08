import sys
import math

class gcode:
    def __init__(self, out = None,
                spindle_speed = 10000,
                horizontal_feed_rate = 60,
                vertical_feed_rate = 30,
                tool_change_height = 30.0,
                rapid_move_height = 3.0,
                rapid_plunge_height = 0.5,
                mill_diameter = 1.0,
                split_arcs = 0.0):
        self._n = 0
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
        self._x_speed = 0.0
        self._y_speed = 0.0
        self._z_speed = 0.0
        self._gm = 0           # 0, 1, 2, 3
        self._f = 100
        self._milling_z = 0.0  # last Z in G1, G2 or G3

        self._distance = 0.0
        self._rapid_distance = 0.0
        self._rapid_time = 0.0
        self._mill_distance = 0.0
        self._mill_time = 0.0

        self._x_max_rate = 1000.0
        self._y_max_rate = 1000.0
        self._z_max_rate = 600.0

        self._x_max_acc = 30.0
        self._y_max_acc = 30.0
        self._z_max_acc = 30.0

        self._horizontal_feed_rate = horizontal_feed_rate
        self._vertical_feed_rate = vertical_feed_rate
        self._tool_change_height = tool_change_height
        self._rapid_move_height = rapid_move_height
        self._rapid_plunge_height = rapid_plunge_height

        self._split_arcs = split_arcs

        if out == None:
            out = sys.stdout

        self._out = out

        self.gcmd(" ".join(sys.argv))
        self.G(94, c="Millimeters per minute feed rate")
        self.G(21, c="Units == Millimeters")
        self.G(90, c="Absolute coordinates")
        self.G(0, S=spindle_speed, c="RPM spindle speed")
        self.G(1, F=horizontal_feed_rate, c="Feedrate")
        self.G(0, Z=tool_change_height, c="Retract to tool change height")
        self.gcmd(T=0) # ?
        self.M(5, c="Spindle stop")
        self.G(4, P=1.0, c="Wait for spindle to stop")
        self.gcmd("MSG, Change tool bit to cutter diameter %gmm)" % mill_diameter)
        # self.M(6, c="Tool change")
        self.M(0, c="Temporary machine stop")
        self.M(3, c="Spindle on clockwise")
        self.G(4, P=1.0, c="Wait for spindle to get up to speed")

        self.retract()

    def retract(self):
        self.G(0, Z=self._rapid_move_height, c='Retract')

    def plunge(self, Z=None):
        if Z == None:
            Z = self._milling_z

        if self._gm == 0 and self._z > Z + self._rapid_plunge_height:
            self.G(0, Z=Z + self._rapid_plunge_height, c='Rapid plunge')

        self.G(1, Z=Z, F=self._vertical_feed_rate, c="Plunge")
        self.G(1, F=self._horizontal_feed_rate, c="Set milling feed rate")

    def end(self):
        self.G(0, Z=self._tool_change_height, c="Retract")
        self.M(5, c="Spindle off")
        self.G(4, P=1.0, c="Wait for spindle to stop")
        self.M(9, c="Coolant off")
        self.M(2, c="Program end")
        self.gcmd("end, rd=%g mm, rt=%g min, md=%g mm, mt=%g min" % (
                    self._rapid_distance, self._rapid_time,
                    self._mill_distance, self._mill_time))
        #self._out.write("%\n")

    def distance_to(self, x, y):
        return math.sqrt( (x - self._x) ** 2 + (y - self._y) ** 2 )

    def G(self, code, **kwargs):
        kwargs['G'] = code
        self.gcmd(**kwargs)

    def M(self, code, **kwargs):
        kwargs['M'] = code
        self.gcmd(**kwargs)

    @staticmethod
    def v2str(v):
        v = "%.4f" % v
        return v.rstrip('0').rstrip('.')

    def gcmd(self, c=None, **kwargs):
        gm = kwargs.get('G', self._gm)
        self._f = kwargs.get('F', self._f)

        if gm in [0, 1, 2, 3]:
            self._gm = gm

        if 'X' in kwargs or 'Y' in kwargs or 'Z' in kwargs:
            x = self._x
            y = self._y
            z = self._z

            self._x = kwargs.get("X", self._x)
            self._y = kwargs.get("Y", self._y)
            self._z = kwargs.get("Z", self._z)

            dx = self._x - x
            dy = self._y - y
            dz = self._z - z

            d = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

            self._distance += d

            if self._gm == 0:
                self._rapid_distance += d
                self._rapid_time += max(abs(self._x - x) / self._x_max_rate,
                                        abs(self._y - y) / self._y_max_rate,
                                        abs(self._z - z) / self._z_max_rate)
            else:
                if self._gm == 2 or self._gm == 3:
                    r = kwargs.get('R', None)
                    if r is None:
                        i = self._x + kwargs.get('I', 0)
                        j = self._y + kwargs.get('J', 0)
                        k = self._z + kwargs.get('K', 0)
                        r = math.sqrt(i ** 2 + j ** 2 + k ** 2)
                    a = 2.0 * math.asin(d / 2.0 / r)
                    d = a * r

                self._mill_distance += d
                self._mill_time += (d / self._f)

        if self._gm != 0 and 'Z' in kwargs:
            self._milling_z = self._z

        args = []

        g = kwargs.pop('G', None)
        if g is not None:
            args.append('G' + gcode.v2str(g))

        args.extend([ n + gcode.v2str(v) for n,v in kwargs.items() ])

        if c:
            args.append("( " + c + " )")

    #    if not 'Z' in kwargs:
    #        args.append("Z=" + str(Z))
    #        Z = Z + 0.1

        self._out.write(" ".join( args ) + "\n")
        self._n += 1

