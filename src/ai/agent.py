# /ai/agent.py
import pymunk
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from config.settings import Settings
import os

# Define collision categories
GROUND_CATEGORY = 0b1
AGENT_CATEGORY = 0b10

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NeuralNetwork, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Tanh()
        )

    def forward(self, x):
        return self.model(x)

    def mutate(self, mutation_rate):
        with torch.no_grad():
            for param in self.parameters():
                mutation_mask = torch.rand_like(param) < mutation_rate
                random_values = torch.randn_like(param) * 0.5
                param += mutation_mask * random_values

class Agent:
    def __init__(self, space, settings, agent_id):
        self.id = agent_id
        self.settings = settings
        self.space = space
        self.create_body()

        # State and action sizes
        num_bodies = len(self.bodies)
        self.input_size = num_bodies * 6  # 6 features per body part
        self.output_size = len(self.motors)  # Number of motors

        # Neural network and optimizer
        self.model = NeuralNetwork(
            input_size=self.input_size,
            hidden_size=self.settings.get('hidden_size'),
            output_size=self.output_size
        )
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.settings.get('learning_rate')
        )
        self.criterion = nn.MSELoss()
        self.fitness = 0  # For tracking agent's performance
        self.start_x = self.bodies[0].position.x

    def create_body(self):
        self.bodies = []
        self.shapes = []
        self.joints = []
        self.motors = []

        x_position = 100  # All agents start at the same x position
        y_position = 300

        # Torso
        mass = 5
        size = (40, 60)
        moment = pymunk.moment_for_box(mass, size)
        torso_body = pymunk.Body(mass, moment)
        torso_body.position = x_position, y_position
        torso_shape = pymunk.Poly.create_box(torso_body, size)
        torso_shape.friction = 1.0
        torso_shape.elasticity = 0.0
        torso_shape.filter = pymunk.ShapeFilter(
            group=self.id + 1,
            categories=AGENT_CATEGORY,
            mask=GROUND_CATEGORY
        )
        # Assign agent reference to the shape
        torso_shape.agent = self
        self.space.add(torso_body, torso_shape)
        self.bodies.append(torso_body)
        self.shapes.append(torso_shape)

        # Left Upper Leg
        mass = 2
        size = (15, 40)
        moment = pymunk.moment_for_box(mass, size)
        l_upper_leg_body = pymunk.Body(mass, moment)
        l_upper_leg_body.position = torso_body.position.x - 15, torso_body.position.y + 50
        l_upper_leg_shape = pymunk.Poly.create_box(l_upper_leg_body, size)
        l_upper_leg_shape.friction = 1.0
        l_upper_leg_shape.elasticity = 0.0
        l_upper_leg_shape.filter = pymunk.ShapeFilter(
            group=self.id + 1,
            categories=AGENT_CATEGORY,
            mask=GROUND_CATEGORY
        )
        l_upper_leg_shape.agent = self
        self.space.add(l_upper_leg_body, l_upper_leg_shape)
        self.bodies.append(l_upper_leg_body)
        self.shapes.append(l_upper_leg_shape)

        # Left Lower Leg
        mass = 1
        size = (10, 30)
        moment = pymunk.moment_for_box(mass, size)
        l_lower_leg_body = pymunk.Body(mass, moment)
        l_lower_leg_body.position = l_upper_leg_body.position.x, l_upper_leg_body.position.y + 35
        l_lower_leg_shape = pymunk.Poly.create_box(l_lower_leg_body, size)
        l_lower_leg_shape.friction = 1.0
        l_lower_leg_shape.elasticity = 0.0
        l_lower_leg_shape.filter = pymunk.ShapeFilter(
            group=self.id + 1,
            categories=AGENT_CATEGORY,
            mask=GROUND_CATEGORY
        )
        l_lower_leg_shape.agent = self
        self.space.add(l_lower_leg_body, l_lower_leg_shape)
        self.bodies.append(l_lower_leg_body)
        self.shapes.append(l_lower_leg_shape)

        # Right Upper Leg
        mass = 2
        size = (15, 40)
        moment = pymunk.moment_for_box(mass, size)
        r_upper_leg_body = pymunk.Body(mass, moment)
        r_upper_leg_body.position = torso_body.position.x + 15, torso_body.position.y + 50
        r_upper_leg_shape = pymunk.Poly.create_box(r_upper_leg_body, size)
        r_upper_leg_shape.friction = 1.0
        r_upper_leg_shape.elasticity = 0.0
        r_upper_leg_shape.filter = pymunk.ShapeFilter(
            group=self.id + 1,
            categories=AGENT_CATEGORY,
            mask=GROUND_CATEGORY
        )
        r_upper_leg_shape.agent = self
        self.space.add(r_upper_leg_body, r_upper_leg_shape)
        self.bodies.append(r_upper_leg_body)
        self.shapes.append(r_upper_leg_shape)

        # Right Lower Leg
        mass = 1
        size = (10, 30)
        moment = pymunk.moment_for_box(mass, size)
        r_lower_leg_body = pymunk.Body(mass, moment)
        r_lower_leg_body.position = r_upper_leg_body.position.x, r_upper_leg_body.position.y + 35
        r_lower_leg_shape = pymunk.Poly.create_box(r_lower_leg_body, size)
        r_lower_leg_shape.friction = 1.0
        r_lower_leg_shape.elasticity = 0.0
        r_lower_leg_shape.filter = pymunk.ShapeFilter(
            group=self.id + 1,
            categories=AGENT_CATEGORY,
            mask=GROUND_CATEGORY
        )
        r_lower_leg_shape.agent = self
        self.space.add(r_lower_leg_body, r_lower_leg_shape)
        self.bodies.append(r_lower_leg_body)
        self.shapes.append(r_lower_leg_shape)

        # Joints and Motors

        # Torso to Left Upper Leg (Hip)
        l_hip_joint = pymunk.PinJoint(torso_body, l_upper_leg_body, (-15, 30), (0, -20))
        self.space.add(l_hip_joint)
        self.joints.append(l_hip_joint)

        l_hip_motor = pymunk.SimpleMotor(torso_body, l_upper_leg_body, 0)
        l_hip_motor.max_force = self.settings.get('max_torque')
        self.space.add(l_hip_motor)
        self.motors.append(l_hip_motor)

        # Left Upper Leg to Lower Leg (Knee)
        l_knee_joint = pymunk.PinJoint(l_upper_leg_body, l_lower_leg_body, (0, 20), (0, -15))
        self.space.add(l_knee_joint)
        self.joints.append(l_knee_joint)

        l_knee_motor = pymunk.SimpleMotor(l_upper_leg_body, l_lower_leg_body, 0)
        l_knee_motor.max_force = self.settings.get('max_torque')
        self.space.add(l_knee_motor)
        self.motors.append(l_knee_motor)

        # Torso to Right Upper Leg (Hip)
        r_hip_joint = pymunk.PinJoint(torso_body, r_upper_leg_body, (15, 30), (0, -20))
        self.space.add(r_hip_joint)
        self.joints.append(r_hip_joint)

        r_hip_motor = pymunk.SimpleMotor(torso_body, r_upper_leg_body, 0)
        r_hip_motor.max_force = self.settings.get('max_torque')
        self.space.add(r_hip_motor)
        self.motors.append(r_hip_motor)

        # Right Upper Leg to Lower Leg (Knee)
        r_knee_joint = pymunk.PinJoint(r_upper_leg_body, r_lower_leg_body, (0, 20), (0, -15))
        self.space.add(r_knee_joint)
        self.joints.append(r_knee_joint)

        r_knee_motor = pymunk.SimpleMotor(r_upper_leg_body, r_lower_leg_body, 0)
        r_knee_motor.max_force = self.settings.get('max_torque')
        self.space.add(r_knee_motor)
        self.motors.append(r_knee_motor)

    def update(self):
        state = self.get_state()
        action = self.choose_action(state)
        self.apply_action(action)
        self.calculate_fitness()

    def get_state(self):
        state = []
        screen_width = self.settings.get('screen_width')
        screen_height = self.settings.get('screen_height')

        for body in self.bodies:
            # Position
            state.append(body.position.x / screen_width)
            state.append(body.position.y / screen_height)
            # Velocity
            state.append(body.velocity.x / 500)
            state.append(body.velocity.y / 500)
            # Angle
            state.append((body.angle % (2 * np.pi)) / (2 * np.pi))
            # Angular Velocity
            state.append(body.angular_velocity / 10)

        return torch.tensor(state, dtype=torch.float32)

    def choose_action(self, state):
        self.model.eval()
        with torch.no_grad():
            action = self.model(state)
        return action

    def apply_action(self, action):
        target_velocity = action.numpy() * self.settings.get('max_motor_velocity')

        for motor, target in zip(self.motors, target_velocity):
            motor.rate = target

    def calculate_fitness(self):
        current_x = self.bodies[0].position.x
        distance = current_x - self.start_x
        self.fitness = distance

    def get_fitness(self):
        return self.fitness

    def get_position(self):
        return self.bodies[0].position

    def save_model(self, filename):
        try:
            torch.save(self.model.state_dict(), filename)
            print(f"Agent {self.id} model saved to {filename}")
        except Exception as e:
            print(f"Error saving model for Agent {self.id}: {e}")  # Optional: print error

    def load_model(self, filename):
        if os.path.exists(filename):
            try:
                self.model.load_state_dict(torch.load(filename))
                print(f"Agent {self.id} model loaded from {filename}")
            except Exception as e:
                print(f"Error loading model for Agent {self.id}: {e}")  # Optional: print error
        else:
            print(f"Model file {filename} does not exist.")  # Optional: print error

    def mutate(self):
        mutation_rate = self.settings.get('mutation_rate')
        self.model.mutate(mutation_rate)

    def reset_position(self):
        # Reset agent's position to starting point
        x_position = 100
        y_position = 300
        for body in self.bodies:
            body.position = x_position, y_position
            body.velocity = 0, 0
            body.angle = 0
            body.angular_velocity = 0
        self.start_x = x_position
        self.fitness = 0

    def remove(self):
        # Remove bodies, shapes, joints, and motors
        for motor in self.motors:
            self.space.remove(motor)
        for joint in self.joints:
            self.space.remove(joint)
        for shape in self.shapes:
            self.space.remove(shape)
        for body in self.bodies:
            self.space.remove(body)
