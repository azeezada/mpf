# Claw controller Scriptlet for Demo Man

from mpf.system.scriptlet import Scriptlet


class Claw(Scriptlet):

    def on_load(self):
        self.machine.switch_controller.add_switch_handler(
            's_elevator_hold', self.get_ball, ms=100)

        if self.machine.switch_controller.is_active('s_elevator_hold'):
            self.get_ball()

        self.machine.events.add_handler('light_claw', self.light_claw)

    def enable(self):
        self.machine.switch_controller.add_switch_handler(
            's_flipper_lower_left', self.move_left)
        self.machine.switch_controller.add_switch_handler(
            's_flipper_lower_left', self.stop_moving, state=0)
        self.machine.switch_controller.add_switch_handler(
            's_flipper_lower_right', self.move_right)
        self.machine.switch_controller.add_switch_handler(
            's_flipper_lower_right', self.stop_moving, state=0)
        self.machine.switch_controller.add_switch_handler(
            's_ball_launch', self.release)
        self.machine.switch_controller.add_switch_handler(
            's_claw_position_1', self.stop_moving)

    def disable(self):
        self.stop_moving()
        self.machine.switch_controller.remove_switch_handler(
            's_flipper_lower_left', self.move_left)
        self.machine.switch_controller.remove_switch_handler(
            's_flipper_lower_left', self.stop_moving, state=0)
        self.machine.switch_controller.remove_switch_handler(
            's_flipper_lower_right', self.move_right)
        self.machine.switch_controller.remove_switch_handler(
            's_flipper_lower_right', self.stop_moving, state=0)
        self.machine.switch_controller.remove_switch_handler(
            's_ball_launch', self.release)
        self.machine.switch_controller.remove_switch_handler(
            's_claw_position_1', self.stop_moving)
        self.machine.switch_controller.remove_switch_handler(
            's_claw_position_1', self.release, state=0)
        self.machine.switch_controller.remove_switch_handler(
            's_claw_position_2', self.release)

    def move_left(self):
        if (self.machine.switch_controller.is_active('s_claw_position_2') and
                self.machine.switch_controller.is_active('s_claw_position_1')):
            return
        self.machine.coils['c_claw_motor_left'].enable()

    def move_right(self):
        if (self.machine.switch_controller.is_active('s_claw_position_1') and
                self.machine.switch_controller.is_inactive('s_claw_position_2')):
            return
        self.machine.coils['c_claw_motor_right'].enable()

    def stop_moving(self):
        self.machine.coils['c_claw_motor_left'].disable()
        self.machine.coils['c_claw_motor_right'].disable()

    def release(self):
        self.machine.coils['c_claw_magnet'].disable()
        self.disable()

    def auto_release(self):
        self.disable()
        if (self.machine.switch_controller.is_active('s_claw_position_2') and
                self.machine.switch_controller.is_active('s_claw_position_1')):
            # move right, drop when switch 1 opens
            self.machine.switch_controller.add_switch_handler(
                's_claw_position_1', self.release, state=0)

        elif (self.machine.switch_controller.is_active('s_claw_position_1') and
                self.machine.switch_controller.is_inactive('s_claw_position_2')):
            # move left, drop when switch 2 closes
            self.machine.switch_controller.add_switch_handler(
                's_claw_position_2', self.release)

        else:
            self.release()

    def get_ball(self):
        if not (self.machine.switch_controller.is_active('s_claw_position_1') and
                self.machine.switch_controller.is_inactive('s_claw_position_2')):
            self.move_right()

            self.machine.switch_controller.add_switch_handler(
                's_claw_position_1', self.do_pickup)
        else:
            self.do_pickup()

    def do_pickup(self):
        self.machine.switch_controller.remove_switch_handler(
            's_claw_position_1', self.do_pickup)
        self.machine.coils['c_claw_magnet'].enable()
        self.machine.coils['c_elevator_motor'].enable()
        self.machine.switch_controller.add_switch_handler('s_elevator_index',
                                                          self.stop_elevator)
        self.enable()

    def stop_elevator(self):
        self.machine.coils['c_elevator_motor'].disable()

    def light_claw(self):
        #self.machine.ball_devices['elevator'].request_ball()
        self.machine.diverters['diverter'].enable()
