# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = [0, 0]
lives = [3, 3]
time = 0
angular_vel = 3
friction_coef = 0.9
ship_velocity = [0, 0]
missile_live = False
explosion_live = False
a_exp = set([])
acc_lam = 2
rock_vel_max = 2
current_angle_vel = [0, 0]
render_scale = 0.5
ship_invincible_time = 60
global_pause_state = True
num_rocks = 20
a_rock = set([])
my_ship = set([])
two_players = False
a_missile = set([])
inelastic_const = 0.9

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated
       
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [85, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 60)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# game initialization function
def initialize():
    global my_ship, a_rock, two_players, score, lives, global_pause_state, global_splash_state
    two_players = False
    my_ship = [Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)]
    a_rock = set([])
    for i in range(num_rocks):
        a_rock.add(rock_spawner())
    score = [0, 0]
    lives = [3, 3]
    global_pause_state = False
    global_splash_state = False

def initialize2():
    global my_ship, a_rock, two_players, score, lives, global_pause_state, global_splash_state
    two_players = True
    my_ship = [Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info, 0)]
    my_ship.append(Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info, 1))
    a_rock = set([])
    for i in range(num_rocks):
        a_rock.add(rock_spawner())
    score = [0, 0]
    lives = [3, 3]
    global_pause_state = False
    global_splash_state = False

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# helper functions for controls
def keydown(key):
    global global_pause_state
    if not global_pause_state or not global_splash_state:
        if key == simplegui.KEY_MAP["left"]:
            my_ship[0].turn(-angular_vel)
        elif key == simplegui.KEY_MAP["right"]:
            my_ship[0].turn(angular_vel)
        elif key == simplegui.KEY_MAP["up"]:
            my_ship[0].thrust(True)
        elif key == simplegui.KEY_MAP["space"]:
            my_ship[0].shoot()
        elif key == simplegui.KEY_MAP["p"]:
            if global_pause_state:
                global_pause_state = False
            else:
                global_pause_state = True
        elif key == simplegui.KEY_MAP["w"]:
            if two_players:
                my_ship[1].thrust(True)
        elif key == simplegui.KEY_MAP["a"]:
            if two_players:
                my_ship[1].turn(-angular_vel)
        elif key == simplegui.KEY_MAP["d"]:
            if two_players:
                my_ship[1].turn(angular_vel)
        elif key == simplegui.KEY_MAP["f"]:
            if two_players:
                my_ship[1].shoot()
    
def keyup(key):
    if not global_splash_state or not global_pause_state:
        if key == simplegui.KEY_MAP["left"]:
            my_ship[0].turn(angular_vel)
        elif key == simplegui.KEY_MAP["right"]:
            my_ship[0].turn(-angular_vel)
        elif key == simplegui.KEY_MAP["up"]:
            my_ship[0].thrust(False)
            ship_thrust_sound.rewind()
        elif key == simplegui.KEY_MAP["w"]:
            if two_players:
                my_ship[1].thrust(False)
        elif key == simplegui.KEY_MAP["a"]:
            if two_players:
                my_ship[1].turn(angular_vel)
        elif key == simplegui.KEY_MAP["d"]:
            if two_players:
                my_ship[1].turn(-angular_vel)

def mouseclick(key):
    global global_splash_state, global_pause_state
    if global_splash_state:
        initialize()
    global_splash_state = False
    global_pause_state = False

def rock_spawner():
    global time
    spawn_ok = False

    while not spawn_ok:
        spawn_ok = True

        rock_pos = [random.randrange(0, WIDTH + 1), random.randrange(0, HEIGHT + 1)]
        
        if len(a_rock) > 0:
            for a in a_rock:
                a_pos = get_pos(a)
                a_rad = get_rad(a)

                rock_spawn_dist = dist(a_pos, rock_pos)
                if rock_spawn_dist <= (a_rad + asteroid_info.get_radius() * 1.5):
                    spawn_ok = False

        for i in range(len(my_ship)):
            ship_spawn_dist = dist(rock_pos, my_ship[i].pos)

            if ship_spawn_dist <= (asteroid_info.get_radius() * 1.5 + my_ship[i].radius):
                spawn_ok = False

    rock_vel = [random.randrange(-rock_vel_max, rock_vel_max) * (1 + time / 3600), random.randrange(-rock_vel_max, rock_vel_max) * (1 + time / 3600)]

    ang = random.randrange(0, 360)
    ang_vel = random.randrange(-3, 3)

    return Sprite(rock_pos, rock_vel, ang, ang_vel, asteroid_image, asteroid_info, None, False, False, -1)

def explosion_spawner(pos, vel):
    return Sprite(pos, vel, 0, 0, explosion_image, explosion_info)

def get_pos(obj):
    return obj.pos

def get_rad(obj):
    return obj.radius

def get_vel(obj):
    return obj.vel

def get_owner(obj):
    return obj.owner

def get_age(obj):
    return obj.age

def get_respawn(obj):
    return obj.respawn

def collision(obj1, obj2, ship = False):
    # determine collision angle
    collision_angle = math.atan2(obj1.pos[1] - obj2.pos[1], obj1.pos[0] - obj2.pos[0])

    # calculate linear velocities
    obj1_v0 = math.sqrt(obj1.vel[0] ** 2 + obj1.vel[1] ** 2)
    obj2_v0 = math.sqrt(obj2.vel[0] ** 2 + obj2.vel[1] ** 2)

    # calculate masses
    obj1_mass = obj1.radius ** 3
    obj2_mass = obj2.radius ** 3

    # transform coordinate system
    obj1_vr = [obj1_v0 * math.cos(math.atan2(obj1.vel[1], obj1.vel[0]) - collision_angle), obj1_v0 * math.sin(math.atan2(obj1.vel[1], obj1.vel[0]) - collision_angle)]
    obj2_vr = [obj2_v0 * math.cos(math.atan2(obj2.vel[1], obj2.vel[0]) - collision_angle), obj2_v0 * math.sin(math.atan2(obj2.vel[1], obj2.vel[0]) - collision_angle)]

    # calculate post-collision x-velocity
    obj1_vfx = (obj1_vr[0] * (obj1_mass - obj2_mass) + 2 * obj2_mass * obj2_vr[0]) / (obj1_mass + obj2_mass)
    obj2_vfx = (obj2_vr[0] * (obj2_mass - obj1_mass) + 2 * obj1_mass * obj1_vr[0]) / (obj1_mass + obj2_mass)

    # calculate post-collision velocity
    obj1_vf = math.sqrt(obj1_vfx ** 2 + obj1_vr[1] ** 2) * inelastic_const
    obj2_vf = math.sqrt(obj2_vfx ** 2 + obj2_vr[1] ** 2) * inelastic_const

    # calculate post-collision angle of travel in original coordinates
    obj1_d2 = math.atan2(obj1_vr[1], obj1_vfx) + collision_angle
    obj2_d2 = math.atan2(obj2_vr[1], obj2_vfx) + collision_angle

    # calculate post-collision x & y velocities
    obj1.vel = [obj1_vf * math.cos(obj1_d2), obj1_vf * math.sin(obj1_d2)]
    obj2.vel = [obj2_vf * math.cos(obj2_d2), obj2_vf * math.sin(obj2_d2)]

    # average spin velocities
    if not ship:
        avg_angular_vel = (obj1.angle_vel + obj2.angle_vel) / 2
        obj1.angle_vel -= avg_angular_vel
        obj2.angle_vel -= avg_angular_vel

def collision_check():
    global score, lives, my_ship, a_rock, a_exp, a_missile
    # checks for collisions between asteroids, ships, and missiles
    collision_set = a_rock.copy()
    for a in a_rock:
        a_pos = get_pos(a)
        a_rad = get_rad(a)
        a_vel = get_vel(a)

        collision_set.remove(a)
        
        if len(collision_set) != 0:
            for c in collision_set:
                c_pos = get_pos(c)
                c_rad = get_rad(c)
                a_c_dist = dist(a_pos, c_pos)                

                if a_c_dist <= (a_rad + c_rad):
                    c_vel = get_vel(c)

                    a_pos_d = [a_pos[0] + a_vel[0], a_pos[1] + a_vel[1]]
                    c_pos_d = [c_pos[0] + c_vel[0], c_pos[1] + c_vel[1]]

                    a_c_dist_d = dist(a_pos_d, c_pos_d)

                    if a_c_dist >= a_c_dist_d:
                        collision(a, c)

        for i in range(len(my_ship)):
            s_pos = get_pos(my_ship[i])
            a_s_dist = dist(a_pos, s_pos)
            s_rad = get_rad(my_ship[i])

            if a_s_dist <= (a_rad + s_rad):
                s_vel = get_vel(my_ship[i])

                a_pos_d = [a_pos[0] + a_vel[0], a_pos[1] + a_vel[1]]
                s_pos_d = [s_pos[0] + s_vel[0], s_pos[1] + s_vel[1]]

                a_s_dist_d = dist(a_pos_d, s_pos_d)

                if a_s_dist >= a_s_dist_d:
                    s_age = get_age(my_ship[i])
                    if s_age <= ship_invincible_time:
                        collision(a, my_ship[i], True)
                    else:
                        e_pos = s_pos
                        e_vel = s_vel
                        a_exp.add(explosion_spawner(e_pos, e_vel))
                        owner = get_owner(my_ship[i])
                        lives[owner] -= 1
                        my_ship[i].pos = [WIDTH / 2, HEIGHT / 2]
                        my_ship[i].age = 0
                        a_rock.remove(a)

        if len(a_missile) > 0:
            for m in a_missile:
                m_pos = get_pos(m)
                m_rad = get_rad(m)
                a_m_dist = dist(a_pos, m_pos)

                if a_m_dist <= (a_rad + m_rad):
                    e_pos = a_pos
                    e_vel = a_vel
                    a_exp.add(explosion_spawner(e_pos, e_vel))

                    a_rock.remove(a)
                    a_rock.add(rock_spawner())
                    a_missile.remove(m)

                    owner = get_owner(m)
                    score[owner] += 1

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info, ship_num = 0):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = angle
        self.angle_vel = current_angle_vel[ship_num]
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.render_size = [self.image_size[0] * render_scale, self.image_size[1] * render_scale]
        self.radius = self.render_size[1] / 2
        self.age = 0
        self.thruster_on = False
        self.missile_live = False
        self.owner = ship_num
        
    def draw(self,canvas):
        if self.age < ship_invincible_time:
            canvas.draw_circle(self.pos, self.radius * 1.1, 2, "rgba(0, 0, 100, 1)", "rgba(0, 100, 100, 0.25)")

        if self.thruster_on:
            canvas.draw_image(self.image, (self.image_center[0] + 91, self.image_center[1]), self.image_size, self.pos, self.render_size, math.radians(self.angle))
        else:
            canvas.draw_image(self.image, (self.image_center[0], self.image_center[1]), self.image_size, self.pos, self.render_size, math.radians(self.angle))

    def update(self):
        if self.age < (ship_invincible_time + 1):
            self.age += 1

        # update angle
        self.angle += self.angle_vel

        global current_angle_vel
        current_angle_vel[self.owner] = self.angle_vel

        # update position
        accel_vector = angle_to_vector(math.radians(self.angle))
        
        if self.thruster_on:
            self.vel = [self.vel[0] + accel_vector[0] * 0.1, self.vel[1] + accel_vector[1] * 0.1]

        self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]

        # friction
        friction_coef = 0.98
        self.vel = [self.vel[0] * friction_coef, self.vel[1] * friction_coef]

        # boundries
        boundry_buffer = 20
        if self.pos[0] > WIDTH + boundry_buffer:
            self.pos[0] = -boundry_buffer
        elif self.pos[0] < -boundry_buffer:
            self.pos[0] = WIDTH + boundry_buffer

        if self.pos[1] > HEIGHT + boundry_buffer:
            self.pos[1] = -boundry_buffer
        elif self.pos[1] < -boundry_buffer:
            self.pos[1] = HEIGHT + boundry_buffer

    def shoot(self):
        missile_vector = angle_to_vector(math.radians(self.angle))
        missile_vel_mult = 3
        missile_pos = [0, 0]
        missile_pos[0] = self.pos[0] + missile_vector[0] * self.render_size[0] / 2
        missile_pos[1] = self.pos[1] + missile_vector[1] * self.render_size[1] / 2
        missile_vel = [self.vel[0] + missile_vel_mult * missile_vector[0], self.vel[1] + missile_vel_mult * missile_vector[1]]

        global a_missile

        self.missile_live = True
        a_missile.add(Sprite(missile_pos, missile_vel, 0, 0, missile_image, missile_info, missile_sound, True, False, self.owner))

    def turn(self, vel):
        self.angle_vel += vel

    def thrust(self, switch):
        self.thruster_on = switch
        if self.thruster_on:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None, missile = False, respawn = False, owned = -1):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.render_size = [self.image_size[0] * render_scale, self.image_size[1] * render_scale]
        self.radius = info.get_radius() * render_scale
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.missile = missile
        self.respawn = respawn
        self.owner = owned
        self.random_scale = (1 - random.randrange(-50, 50) / 100)

        if sound:
            sound.rewind()
            sound.play()

        if self.missile:
            self.radius = info.get_radius()
            self.render_size = self.image_size
        elif self.animated:
            self.render_size = self.image_size
        else:
            self.render_size[0] *= self.random_scale
            self.render_size[1] *= self.random_scale
            self.radius *= self.random_scale
   
    def draw(self, canvas):
        if self.lifespan != float('inf'):
            if self.age < self.lifespan:
                if self.animated:
                    img_center = [self.image_center[0] + self.image_size[0] * self.age, self.image_center[1]]
                    canvas.draw_image(self.image, img_center, self.image_size, self.pos, self.render_size, math.radians(self.angle))
                else:
                    canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.render_size, math.radians(self.angle))
            else:
                self.respawn = True

        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.render_size, math.radians(self.angle))

    def update(self):
        # update position and angle
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel

        # update age
        if self.lifespan != float('inf'):
            self.age += 1

        # boundries
        boundry_buffer = 20
        if self.pos[0] > WIDTH + boundry_buffer:
            self.pos[0] = -boundry_buffer
        elif self.pos[0] < -boundry_buffer:
            self.pos[0] = WIDTH + boundry_buffer

        if self.pos[1] > HEIGHT + boundry_buffer:
            self.pos[1] = -boundry_buffer
        elif self.pos[1] < -boundry_buffer:
            self.pos[1] = HEIGHT + boundry_buffer
           
def draw(canvas):
    global time, global_pause_state, global_splash_state, my_ship, a_rock, a_missile, a_exp
    
    # animiate background
    if not global_pause_state:
        time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    if wtime == 0:
        wtime = 0.1
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]], [size[0] - 2 * wtime, size[1]], 
                                [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], [WIDTH - 2.5 * wtime, HEIGHT])
    canvas.draw_image(debris_image, [size[0] - wtime, center[1]], [2 * wtime, size[1]], 
                                [1.25 * wtime, HEIGHT / 2], [2.5 * wtime, HEIGHT])

    # draw ship
    for i in range(len(my_ship)):
        my_ship[i].draw(canvas)
        if not global_pause_state:
            my_ship[i].update()
        if lives[i] <= 0:
            global_splash_state = True
            a_rock = set([])
            a_missile = set([])
            a_exp = set([])

    # draw rocks
    for a in a_rock:
        a.draw(canvas)
        if not global_pause_state:
            a.update()

    # draw missiles
    if len(a_missile) > 0:
        for a in a_missile:
            respawn = get_respawn(a)
            if respawn:
                a_missile.remove(a)
            else:
                a.draw(canvas)
                if not global_pause_state:
                    a.update()

    # draw explosion
    if len(a_exp) > 0:
        for a in a_exp:
            respawn = get_respawn(a)
            if respawn:
                a_exp.remove(a)
            else:
                a.draw(canvas)
                a.update()

    collision_check()

    # draw lives and score
    lives_text = "Lives: " + str(lives[0])
    canvas.draw_text(lives_text, (50, 50), 24, "White")
    if two_players:
        lives_text2 = "Lives: " + str(lives[1])
        canvas.draw_text(lives_text2, (50, 75), 24, "White")

    score_text = "Score: " + str(score[0])
    canvas.draw_text(score_text, (650, 50), 24, "White")
    if two_players:
        score_text2 = "Score: " + str(score[1])
        canvas.draw_text(score_text2, (650, 75), 24, "White")

    # draw pause
    if global_pause_state:
        canvas.draw_text("P A U S E D", [WIDTH / 3, HEIGHT / 2], 64, "White")

    # draw splash
    if global_splash_state:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], splash_info.get_size())
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# register handlers
frame.set_draw_handler(draw)

# timer = simplegui.create_timer(1000.0, rock_spawner)

frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("1 Player Start", initialize)
frame.add_button("2 Player Start", initialize2)
frame.set_mouseclick_handler(mouseclick)

# get things rolling
# timer.start()
global_splash_state = True
global_pause_state = True

frame.start()
