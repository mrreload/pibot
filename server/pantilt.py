from Adafruit_PWM_Servo_Driver import PWM
'''
Tiny mini Pan/Tilt library
By default, tilt is on channel 1
and pan on channel 0
'''
servo = PWM(0x40)
servo.setPWMFreq(50)

TILT = 0
PAN  = 3

pan_center = 90
tilt_center = 50
pan_per_deg = 2.288888889
tilt_per_deg = 2.65
servo_pan_left = 163
servo_pan_right = 575
servo_tilt_up = 200
servo_tilt_down = 465

def pan(deg):
	print("Pan " + str(deg))
  	#cali(PAN,deg)
	pwm = getPWM(deg,pan_per_deg,servo_pan_left)
	print(str(pwm))
	servo.setPWM(PAN, 0, getPWM(deg,pan_per_deg,servo_pan_left))
def tilt(deg):
	print("Tilt " + str(deg))
	_turn2(TILT,deg)

def _turn(s,deg):
  	pwm = 451.0 + ((deg/180.0) * 1000.0)

  	pwm = (4096.0/20000.0) * pwm
  	pwm = int(pwm)
  	print(str(pwm))

  	servo.setPWM(s, 0, pwm)

def _turn2(s,deg):
  	pwm = (float(deg) * tilt_per_deg) + float(servo_tilt_up)
  	print("Moving: " + str(pwm))
  	pwm = int(pwm)
  	servo.setPWM(s, 0, pwm)

def reset():
	pan(pan_center)
	tilt(tilt_center)
	
def _turn3(s,deg):
  	pwm = (float(deg) * pan_per_deg) + float(servo_pan_left)
  	print("Moving: " + str(pwm))
  	pwm = int(pwm)
  	servo.setPWM(s, 0, pwm)

def cali(s,pnt):
	print("Move to: " + str(pnt))
	servo.setPWM(s, 0, pnt)

def getPWM(deg,offset,srv_min):
	pwm = (float(deg) * offset) + float(srv_min)
	return int(pwm)

