import pygame
import math
import csv
import os

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)

G_scaled = 6.67430e-11

pixels_per_km = 0.01

earth_values = {
    'planet_mass': 5.972e24,
    'planet_radius': 6371e3,
    'spacecraft_mass': 1000,
    'position': (width // 2 + 300, height // 2),
    'velocity': (0, -80 * pixels_per_km)
}
test_spacecraft_values = {
    'planet_mass': 5.972e24,
    'planet_radius': 6371e3,
    'spacecraft_mass': 500,
    'position': (width // 2 + 250, height // 2),
    'velocity': (0, -100 * pixels_per_km)
}

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_valid_input(prompt, is_positive=True):
    while True:
        user_input = input(prompt)
        if is_number(user_input):
            user_input = float(user_input)
            if not is_positive or user_input >= 0:
                return user_input
            else:
                print("Please enter a positive number.")
        else:
            print("Invalid input. Please enter a number.")

def display_menu():
    print("\nSelect a Test Configuration:")
    print("1 - Earth")
    print("2 - Test Spacecraft")
    print("3 - Custom Input")
    print("Enter 'quit' to exit")

def get_user_choice():
    while True:
        display_menu()
        choice = input("Enter your choice (1, 2, 3, or 'quit'): ").strip().lower()

        if choice in ['1', '2', '3', 'quit']:
            return choice
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 'quit'.")

def get_custom_input():
    print("\nEnter custom simulation values:")
    planet_mass = get_valid_input("Enter planet mass (kg): ")
    planet_radius = get_valid_input("Enter planet radius (km): ") * pixels_per_km
    spacecraft_mass = get_valid_input("Enter spacecraft mass (kg): ")
    position_x = get_valid_input("Enter spacecraft starting x position (km): ") * pixels_per_km
    position_y = get_valid_input("Enter spacecraft starting y position (km): ") * pixels_per_km
    velocity_x = get_valid_input("Enter spacecraft starting x velocity (km/s): ") * pixels_per_km
    velocity_y = get_valid_input("Enter spacecraft starting y velocity (km/s): ") * pixels_per_km

    return {
        'planet_mass': planet_mass,
        'planet_radius': planet_radius,
        'spacecraft_mass': spacecraft_mass,
        'position': (width // 2 + position_x, height // 2 + position_y),
        'velocity': (velocity_x, velocity_y)
    }

def calculate_gravitational_force(pos1, pos2, m1, m2):
    distance_x = pos2[0] - pos1[0]
    distance_y = pos2[1] - pos1[1]
    distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

    force = G_scaled * (m1 * m2) / distance ** 2
    force_x = force * (distance_x / distance)
    force_y = force * (distance_y / distance)

    return force_x, force_y, distance

def update_position(vel, pos):
    pos[0] += vel[0]
    pos[1] += vel[1]

def update_velocity(force, vel, mass):
    acceleration_x = force[0] / mass
    acceleration_y = force[1] / mass
    vel[0] += acceleration_x
    vel[1] += acceleration_y
    return acceleration_x, acceleration_y

def run_simulation(chosen_values):
    M_scaled = chosen_values['planet_mass'] * 1e-12
    planet_radius = 40
    m = chosen_values['spacecraft_mass']
    satellite_pos = list(chosen_values['position'])
    satellite_vel = list(chosen_values['velocity'])

    csv_filename = os.path.join('simulation_data.csv')
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Frame", "Satellite X (km)", "Satellite Y (km)", "Velocity X (km/s)", "Velocity Y (km/s)",
                         "Force X (N)", "Force Y (N)", "Total Distance (km)", "Total Velocity (km/s)", "Total Acceleration (km/s²)"])

    frame_count = 0
    running = True
    planet_pos = (width // 2, height // 2)
    last_acceleration_x, last_acceleration_y = 0, 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(black)

        pygame.draw.circle(screen, blue, planet_pos, planet_radius)
        pygame.draw.circle(screen, white, (int(satellite_pos[0]), int(satellite_pos[1])), 5)

        force_x, force_y, total_distance = calculate_gravitational_force(satellite_pos, planet_pos, m, M_scaled)
        acceleration_x, acceleration_y = update_velocity((force_x, force_y), satellite_vel, m)
        update_position(satellite_vel, satellite_pos)

        total_velocity = math.sqrt(satellite_vel[0]**2 + satellite_vel[1]**2)
        total_acceleration = math.sqrt((acceleration_x - last_acceleration_x)**2 + (acceleration_y - last_acceleration_y)**2)
        last_acceleration_x, last_acceleration_y = acceleration_x, acceleration_y

        with open(csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                [frame_count,
                 satellite_pos[0] / pixels_per_km, satellite_pos[1] / pixels_per_km,
                 satellite_vel[0] / pixels_per_km, satellite_vel[1] / pixels_per_km,
                 force_x, force_y,
                 total_distance / pixels_per_km,
                 total_velocity / pixels_per_km,
                 total_acceleration / (pixels_per_km * pixels_per_km)])

        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    pygame.quit()


def main():
    while True:
        user_choice = get_user_choice()

        if user_choice == '1':
            chosen_values = earth_values
            break
        elif user_choice == '2':
            chosen_values = test_spacecraft_values
            break
        elif user_choice == '3':
            chosen_values = get_custom_input()
            break
        elif user_choice == 'quit':
            print("Exiting program.")
            return

    run_simulation(chosen_values)

if __name__ == "__main__":
    main()