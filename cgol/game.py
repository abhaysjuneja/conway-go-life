import time

import pygame


class GameOfLife:
    # Window Constants
    FPS = 20

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)

    # Grid Constants
    FILL_PADDING = 1
    DIRECTIONS = [
        (-1, -1),
        (-1, 0),
        (-1, 1),  # Top row
        (0, -1),
        (0, 1),  # Left and Right
        (1, -1),
        (1, 0),
        (1, 1),
    ]  # Bottom row

    # Toolbar Constants
    TOOLBAR_HEIGHT = 30
    BUTTON_HEIGHT = 25
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT_PADDING = 5
    BUTTON_WIDTH_PADDING = 10
    BUTTON_EFFECT_DURATION = 0.2

    def __init__(self, grid_size=25, cell_size=30):
        """Initialize the Game of Life."""
        pygame.init()

        # Grid properties
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.width = self.grid_size * self.cell_size
        self.height = (
            self.grid_size * self.cell_size + self.TOOLBAR_HEIGHT
        )  # Add toolbar space

        # Pygame window setup
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Conway's Game of Life")

        # Initialize grid (2D list)
        self.grid = self.initialize_grid()
        self.window_alive = True  # if the game window is up and running
        self.is_running = False  # if the simulation is running.

        # Toolbar buttons (dictionary with button labels and positions)
        self.buttons = self.initialize_buttons()

        # Pygame font
        self.font = pygame.font.Font(None, 24)

    def initialize_buttons(self):
        """Initializes toolbar buttons."""
        return {
            "Start": pygame.Rect(
                self.BUTTON_WIDTH_PADDING,
                self.BUTTON_HEIGHT_PADDING,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
            ),
            "Pause": pygame.Rect(
                2 * self.BUTTON_WIDTH_PADDING + self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT_PADDING,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
            ),
            "End": pygame.Rect(
                3 * self.BUTTON_WIDTH_PADDING + 2 * self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT_PADDING,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
            ),
        }

    def initialize_grid(self):
        """return the initial state of the grid - a clear one"""
        return self.make_clear_grid()

    def make_clear_grid(self):
        """clear the grid to an empty one"""
        return [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def draw_button(self, text, rect):
        """Draws an individual toolbar button."""
        pygame.draw.rect(self.screen, self.WHITE, rect)  # Button background
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)  # Button border
        label = self.font.render(text, True, self.BLACK)
        self.screen.blit(label, (rect.x + 10, rect.y + 5))  # Draw text inside button

    def draw_toolbar(self):
        """Draw the toolbar with buttons."""
        pygame.draw.rect(
            self.screen, self.GRAY, (0, 0, self.width, self.TOOLBAR_HEIGHT)
        )  # Toolbar bg

        # Draw buttons
        for text, rect in self.buttons.items():
            self.draw_button(text, rect)

    def draw_grid(self):
        """Draw the grid below the toolbar."""
        self.screen.fill(
            self.BLUE, (0, self.TOOLBAR_HEIGHT, self.width, self.height)
        )  # Clear grid area

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = pygame.Rect(
                    col * self.cell_size + self.FILL_PADDING,
                    row * self.cell_size
                    + self.FILL_PADDING
                    + self.TOOLBAR_HEIGHT,  # Offset for toolbar
                    self.cell_size - self.FILL_PADDING,
                    self.cell_size - self.FILL_PADDING,
                )
                if self.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, self.WHITE, rect)  # Draw filled cell
                pygame.draw.rect(self.screen, self.WHITE, rect, 1)  # Draw grid lines

    def start_simulation(self):
        """Start the Conway's Game of Life simulation on the current grid state"""
        self.is_running = True

    def pause_simulation(self):
        """Pause the Conway's Game of Life simulation on the current grid state"""
        self.is_running = False

    def end_simulation(self):
        """End the Conway's Game of Life simulation and clear the grid"""
        self.grid = self.make_clear_grid()
        self.is_running = False

    def handle_mouse_click(self, pygame_event):
        """Routes mouse clicks to the correct handler."""
        x, y = pygame_event.pos  # Get mouse click position

        if y < self.TOOLBAR_HEIGHT:
            self.handle_toolbar_click(x, y)
        else:
            self.handle_grid_click(x, y)

    def handle_toolbar_click(self, x, y):
        """Handles toolbar button clicks."""
        for text, rect in self.buttons.items():
            if rect.collidepoint(x, y):
                self.flash_button(text)
                if text == "Start":
                    self.start_simulation()
                elif text == "Pause":
                    self.pause_simulation()
                elif text == "End":
                    self.end_simulation()
                return

    def handle_grid_click(self, x, y):
        """Handles cell toggling in the grid."""
        row = (y - self.TOOLBAR_HEIGHT) // self.cell_size
        col = x // self.cell_size

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            self.grid[row][col] = 1 - self.grid[row][col]  # Toggle cell state

    def flash_button(self, button_text):
        """Flashes a button green when clicked, then restores its original color."""
        button_rect = self.buttons[button_text]

        # Draw button in green
        pygame.draw.rect(self.screen, (0, 255, 0), button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)  # Redraw border

        # Render button text again
        label = self.font.render(button_text, True, self.BLACK)
        self.screen.blit(label, (button_rect.x + 10, button_rect.y + 5))

        pygame.display.flip()  # Update screen
        time.sleep(self.BUTTON_EFFECT_DURATION)  # Flash effect duration (100ms)

        self.draw_toolbar()  # Restore the original button
        pygame.display.flip()  # Refresh screen

    def count_neighbors(self, row, col):
        """Returns the number of alive neighbors for a given cell using toroidal wrapping."""
        count = 0
        for dr, dc in self.DIRECTIONS:
            r = (row + dr) % self.grid_size  # Wrap vertically
            c = (col + dc) % self.grid_size  # Wrap horizontally
            count += self.grid[r][c]  # Add 1 if the neighbor is alive

        return count

    def apply_rules(self):
        """Applies the Game of Life rules to compute the next state of the grid."""
        new_grid = [
            [0 for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]  # Create a new grid

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                neighbors = self.count_neighbors(row, col)
                cell = self.grid[row][col]

                # Apply the rules
                if cell == 1 and (
                    neighbors < 2 or neighbors > 3
                ):  # Underpopulation / Overpopulation
                    new_grid[row][col] = 0
                elif cell == 0 and neighbors == 3:  # Reproduction
                    new_grid[row][col] = 1
                else:  # Stays the same
                    new_grid[row][col] = cell

        return new_grid  # Return the computed grid

    def update_grid(self):
        """Updates the grid state after computing the next iteration."""

        self.grid = self.apply_rules()

    def run(self):
        """Main loop to run the game."""

        clock = pygame.time.Clock()
        while self.window_alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.window_alive = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event)

            if self.is_running:
                self.update_grid()

            self.draw_toolbar()
            self.draw_grid()
            pygame.display.flip()
            clock.tick(self.FPS)

        pygame.quit()


# Run the game
if __name__ == "__main__":
    GRID_SIZE = 50
    CELL_SIZE = 15
    game = GameOfLife(grid_size=GRID_SIZE, cell_size=CELL_SIZE)
    game.run()
