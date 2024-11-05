import pygame
import pymunk
from pymunk.pygame_util import DrawOptions
from ai.agent import Agent
from gui.gui import GUI
from config.settings import Settings
from game.camera import Camera
import os
import time

# Define collision categories as class-level constants
class CollisionCategory:
    GROUND = 0b1
    AGENT = 0b10

class CustomDrawOptions(DrawOptions):
    """Enhanced drawing options for PyMunk shapes"""
    def __init__(self, surface, agents, best_agent, enable_transparency):
        super().__init__(surface)
        self.agents = agents
        self.best_agent = best_agent
        self.enable_transparency = enable_transparency
        
        # Cache colors for better performance
        self.colors = {
            'best_agent': (0, 0, 255),
            'regular_agent': {
                'transparent': (255, 0, 0, 100),
                'opaque': (255, 0, 0)
            },
            'default': (0, 0, 0)
        }

    def draw_shape(self, shape):
        """Enhanced shape drawing with color management"""
        # Determine shape color
        if hasattr(shape, 'agent'):
            if shape.agent == self.best_agent:
                color = self.colors['best_agent']
            else:
                color = (self.colors['regular_agent']['transparent'] 
                        if self.enable_transparency 
                        else self.colors['regular_agent']['opaque'])
        else:
            color = self.colors['default']

        # Draw based on shape type
        if isinstance(shape, pymunk.Segment):
            self._draw_segment(shape, color)
        elif isinstance(shape, pymunk.Poly):
            self._draw_polygon(shape, color)
        elif isinstance(shape, pymunk.Circle):
            self._draw_circle(shape, color)

    def _draw_segment(self, shape, color):
        """Draw segment shapes"""
        body = shape.body
        pv1 = self.transform_point(body.position + shape.a.rotated(body.angle))
        pv2 = self.transform_point(body.position + shape.b.rotated(body.angle))
        pygame.draw.lines(self.surface, color[:3], False, [pv1, pv2], 
                         int(shape.radius))

    def _draw_polygon(self, shape, color):
        """Draw polygon shapes"""
        vertices = [self.transform_point(v.rotated(shape.body.angle) + 
                   shape.body.position) for v in shape.get_vertices()]
        pygame.draw.polygon(self.surface, color[:3], vertices)

    def _draw_circle(self, shape, color):
        """Draw circle shapes"""
        pos = self.transform_point(shape.body.position)
        pygame.draw.circle(self.surface, color[:3], 
                         (int(pos.x), int(pos.y)), int(shape.radius))

class Game:
    """Main game class with enhanced organization and features"""
    def __init__(self):
        self.init_pygame()
        self.init_settings()
        self.init_simulation()
        self.init_display()
        self.init_state()

    def init_pygame(self):
        """Initialize Pygame"""
        pygame.init()
        self.clock = pygame.time.Clock()

    def init_settings(self):
        """Initialize game settings"""
        self.settings = Settings()
        self.screen_width = self.settings.get('screen_width')
        self.screen_height = self.settings.get('screen_height')

    def init_simulation(self):
        """Initialize physics simulation"""
        self.space = pymunk.Space()
        self.space.gravity = (0.0, self.settings.get('gravity'))
        self.create_ground()

    def init_display(self):
        """Initialize display and UI components"""
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("AI Evolution Game")
        self.gui = GUI(self.settings)
        self.camera = Camera(self.screen_width, self.screen_height)

    def init_state(self):
        """Initialize game state"""
        self.running = True
        self.agents = []
        self.best_agent = None
        self.generation = self.settings.get('generation')
        # Initialize timing variables
        self.iteration_start_time = None
        self.pause_start_time = None
        self.accumulated_time = 0
        self.paused = False
        self.create_agents()

    def create_ground(self):
        """Create the game environment with ground"""
        static_body = self.space.static_body
        ground_y = self.screen_height - 50
        
        ground = pymunk.Segment(
            static_body,
            (-1000, ground_y),
            (10000, ground_y),
            5.0
        )
        
        ground.friction = 1.0
        ground.elasticity = 0.0
        ground.filter = pymunk.ShapeFilter(categories=CollisionCategory.GROUND)
        self.space.add(ground)

    def create_agents(self):
        """Create and initialize agents"""
        self.agents = []
        batch_size = self.settings.get('batch_size')
        
        for i in range(batch_size):
            agent = Agent(self.space, self.settings, agent_id=i)
            self.agents.append(agent)
        
        self.best_agent = None

    def reset_agents(self):
        """Reset all agents"""
        for agent in self.agents:
            agent.remove()
        self.create_agents()

    def run(self):
        """Main game loop with improved organization"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            self.handle_events()
            
            if self.settings.get('running') and not self.paused:
                self.update(delta_time)
            
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
            else:
                self.handle_game_event(event)

        self.handle_continuous_input()
        self.handle_gui_state()

    def handle_resize(self, width, height):
        """Handle window resize events"""
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )
        self.camera.resize(width, height)
        self.gui.resize(width, height)

    def handle_game_event(self, event):
        """Handle specific game events"""
        # Handle camera movement with menu visibility check
        self.camera.handle_event(event, self.gui.settings_menu.visible)
        # Handle GUI events
        self.gui.handle_event(event)

    def handle_continuous_input(self):
        """Handle continuous keyboard input"""
        keys = pygame.key.get_pressed()
        
        if not self.gui.settings_menu.visible:
            camera_speed = self.camera.speed
            if keys[pygame.K_LEFT]:
                self.camera.move(-camera_speed, 0)
            if keys[pygame.K_RIGHT]:
                self.camera.move(camera_speed, 0)
            if keys[pygame.K_UP]:
                self.camera.move(0, -camera_speed)
            if keys[pygame.K_DOWN]:
                self.camera.move(0, camera_speed)

    def handle_gui_state(self):
        """Handle GUI state changes with improved pause handling"""
        self.gui.update(self.clock.get_time() / 1000.0)
        
        if self.gui.load_requested:
            self.load_generation()
            self.gui.load_requested = False
            
        if self.gui.pause_requested is not None:
            if self.gui.pause_requested != self.paused:  # Only handle state changes
                if self.gui.pause_requested:  # Pausing
                    if self.iteration_start_time is not None:
                        self.pause_start_time = time.time()
                        # Store current elapsed time
                        self.accumulated_time += self.pause_start_time - self.iteration_start_time
                else:  # Unpausing
                    if self.pause_start_time is not None:
                        self.iteration_start_time = time.time()
                        self.pause_start_time = None
                    elif self.iteration_start_time is None:
                        # First start of simulation
                        self.iteration_start_time = time.time()
                        self.accumulated_time = 0
            
            self.paused = self.gui.pause_requested
            self.gui.pause_requested = None
                
        if self.gui.stop_requested:
            self.settings.set('running', False)
            self.iteration_start_time = None
            self.pause_start_time = None
            self.accumulated_time = 0
            self.reset_agents()
            self.gui.stop_requested = False

    def update(self, delta_time):
        """Update game state with corrected time tracking"""
        # Initialize timer when simulation starts running
        if self.iteration_start_time is None and self.settings.get('running'):
            self.iteration_start_time = time.time()
            self.accumulated_time = 0
            self.pause_start_time = None
        
        if self.iteration_start_time is not None and not self.paused:
            current_time = time.time()
            total_elapsed_time = self.accumulated_time
            if not self.paused:
                total_elapsed_time += current_time - self.iteration_start_time
                
            iteration_time = self.settings.get('iteration_time')

            # Update agents and physics
            for agent in self.agents:
                agent.update()
            self.space.step(1/60.0)

            # Check if iteration is complete
            if total_elapsed_time >= iteration_time:
                self.next_generation()

    def draw(self):
        """Render the game"""
        self.screen.fill((255, 255, 255))
        self.draw_agents()
        self.draw_ui()

    def draw_agents(self):
        """Draw all agents"""
        enable_transparency = self.settings.get('enable_transparency')
        
        # Create surface for agents
        if enable_transparency:
            agent_surface = pygame.Surface(
                (self.screen_width, self.screen_height), 
                pygame.SRCALPHA
            )
        else:
            agent_surface = self.screen

        # Setup draw options
        draw_options = CustomDrawOptions(
            agent_surface,
            self.agents,
            self.best_agent,
            enable_transparency
        )

        # Apply camera transform
        original_transform = draw_options.transform
        draw_options.transform = original_transform.translated(
            self.camera.offset.x,
            self.camera.offset.y
        )

        # Draw physics objects
        self.space.debug_draw(draw_options)
        draw_options.transform = original_transform

        # Blit agent surface if using transparency
        if enable_transparency:
            self.screen.blit(agent_surface, (0, 0))

    def draw_ui(self):
        """Draw UI elements"""
        self.gui.draw(self.screen)
        
        best_x = self.best_agent.get_position().x if self.best_agent else 0
        offset = best_x - self.screen_width / 2
        
        self.display_agent_info()
        self.display_iteration_timer()

    def display_agent_info(self):
        """Display agent statistics"""
        font = pygame.font.SysFont(None, 24)
        
        # Calculate average fitness
        total_fitness = sum(agent.get_fitness() for agent in self.agents)
        avg_fitness = total_fitness / len(self.agents) if self.agents else 0
        
        # Render stats
        stats = [
            (f"Average Fitness: {avg_fitness:.2f}", (self.screen_width - 220, 30)),
            (f"Generation: {self.generation}", (self.screen_width - 220, 10))
        ]
        
        for text, pos in stats:
            surf = font.render(text, True, (0, 0, 0))
            self.screen.blit(surf, pos)

    def display_iteration_timer(self):
        """Display iteration timer with improved pause handling"""
        font = pygame.font.SysFont(None, 24)
        
        if self.iteration_start_time is not None and self.settings.get('running'):
            current_time = time.time()
            total_elapsed_time = self.accumulated_time
            
            if self.paused:
                if self.pause_start_time is not None:
                    # When paused, don't add current time
                    pass
            else:
                # When running, add the current period
                total_elapsed_time += current_time - self.iteration_start_time
            
            time_left = max(0, self.settings.get('iteration_time') - total_elapsed_time)
            text = f"Iteration Time Left: {time_left:.1f}s"
        else:
            text = "Timer: Waiting to Start"
        
        timer_text = font.render(text, True, (0, 0, 0))
        self.screen.blit(timer_text, (self.screen_width - 220, 50))

    def next_generation(self):
        """Handle generation transition with timer reset"""
        # Sort agents by fitness
        self.agents.sort(key=lambda agent: agent.get_fitness(), reverse=True)
        self.best_agent = self.agents[0]

        # Save best agent
        model_path = os.path.join('models', f'generation_{self.generation}.pth')
        self.best_agent.save_model(model_path)

        # Increment generation
        self.generation += 1
        self.settings.set('generation', self.generation)

        # Reset and mutate agents
        self.reset_agents()
        for agent in self.agents:
            agent.load_model(model_path)
            agent.mutate()
            agent.reset_position()
        
        # Reset timing variables for next generation
        self.iteration_start_time = time.time()
        self.accumulated_time = 0
        self.pause_start_time = None

    def load_generation(self):
        """Load a saved generation"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        
        model_path = filedialog.askopenfilename(
            initialdir="models",
            title="Select Model File",
            filetypes=(("PyTorch Models", "*.pth"), ("All Files", "*.*"))
        )
        
        root.update()
        root.destroy()

        if model_path and os.path.exists(model_path):
            try:
                # Parse generation number from filename
                generation_num = int(os.path.basename(model_path).split('_')[1].split('.')[0])
                
                # Update game state
                self.generation = generation_num
                self.settings.set('generation', self.generation)
                
                # Reset and load agents
                self.reset_agents()
                for agent in self.agents:
                    agent.load_model(model_path)
                    agent.reset_position()
                    
# Reset timers
                self.iteration_start_time = None
                self.pause_start_time = None
                self.accumulated_time = 0
                self.paused = False
                    
            except (IndexError, ValueError) as e:
                print(f"Error parsing generation number from file name: {e}")
        else:
            print("Invalid model path selected.")

    def reset_agents(self):
        """Reset all agents"""
        for agent in self.agents:
            agent.remove()
        self.create_agents()

    def create_agents(self):
        """Create and initialize agents"""
        self.agents = []
        batch_size = self.settings.get('batch_size')
        
        for i in range(batch_size):
            agent = Agent(self.space, self.settings, agent_id=i)
            self.agents.append(agent)
        
        self.best_agent = None