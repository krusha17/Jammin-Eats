
-- Create the database
CREATE DATABASE JamminEats;
GO

USE JamminEats;
GO

-- Create Players table
CREATE TABLE Players (
    player_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(100) NULL,
    password_hash NVARCHAR(256) NOT NULL,
    date_registered DATETIME DEFAULT GETDATE(),
    last_login DATETIME NULL,
    high_score INT DEFAULT 0,
    is_active BIT DEFAULT 1
);

-- Create PlayerCharacters table
CREATE TABLE PlayerCharacters (
    character_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    character_name NVARCHAR(50) NOT NULL,
    character_type NVARCHAR(50) NOT NULL DEFAULT 'kai', -- From the code, default character is 'kai'
    speed FLOAT DEFAULT 200.0, -- Default speed from your code
    has_truck BIT DEFAULT 0, -- From your code: self.has_truck = False
    CONSTRAINT FK_PlayerCharacters_Players FOREIGN KEY (player_id) REFERENCES Players(player_id)
);

-- Create GameLevels table
CREATE TABLE GameLevels (
    level_id INT IDENTITY(1,1) PRIMARY KEY,
    level_name NVARCHAR(50) NOT NULL,
    background_image NVARCHAR(200) NULL, -- Path to background image
    width INT DEFAULT 768, -- From your code WIDTH = 768
    height INT DEFAULT 768, -- From your code HEIGHT = 768
    customer_spawn_rate FLOAT DEFAULT 5.0, -- From your code: customer_spawn_rate = 5
    time_limit INT NULL, -- NULL means no time limit
    missed_deliveries_limit INT DEFAULT 10, -- Game over condition from your code
    description NVARCHAR(500) NULL
);

-- Create FoodTypes table
CREATE TABLE FoodTypes (
    food_id INT IDENTITY(1,1) PRIMARY KEY,
    food_name NVARCHAR(50) NOT NULL,
    display_name NVARCHAR(100) NOT NULL, -- Eg. "Tropical Pizza Slice"
    speed INT DEFAULT 300, -- From your code: self.speed = 300
    lifespan FLOAT DEFAULT 2.0, -- From your code: self.lifespan = 2.0
    color_r INT DEFAULT 255,
    color_g INT DEFAULT 255,
    color_b INT DEFAULT 255,
    sprite_path NVARCHAR(200) NULL -- Path to food sprite image
);

-- Create CustomerTypes table
CREATE TABLE CustomerTypes (
    customer_type_id INT IDENTITY(1,1) PRIMARY KEY,
    type_name NVARCHAR(50) NOT NULL,
    min_patience FLOAT DEFAULT 10.0, -- From your code: random.uniform(10, 20)
    max_patience FLOAT DEFAULT 20.0,
    sprite_path NVARCHAR(200) NULL,
    color_r INT DEFAULT 200,
    color_g INT DEFAULT 200,
    color_b INT DEFAULT 200 -- From your code: self.color = (random colors)
);

-- Create GameSessions table
CREATE TABLE GameSessions (
    session_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    character_id INT NOT NULL,
    level_id INT NOT NULL,
    start_time DATETIME DEFAULT GETDATE(),
    end_time DATETIME NULL,
    duration_seconds INT NULL, -- Total game time in seconds
    final_score INT DEFAULT 0,
    deliveries_made INT DEFAULT 0,
    customers_missed INT DEFAULT 0,
    is_completed BIT DEFAULT 0,
    CONSTRAINT FK_GameSessions_Players FOREIGN KEY (player_id) REFERENCES Players(player_id),
    CONSTRAINT FK_GameSessions_Characters FOREIGN KEY (character_id) REFERENCES PlayerCharacters(character_id),
    CONSTRAINT FK_GameSessions_Levels FOREIGN KEY (level_id) REFERENCES GameLevels(level_id)
);

-- Create Deliveries table to track food deliveries during gameplay
CREATE TABLE Deliveries (
    delivery_id INT IDENTITY(1,1) PRIMARY KEY,
    session_id INT NOT NULL,
    food_id INT NOT NULL,
    delivery_time DATETIME DEFAULT GETDATE(),
    matched_preference BIT DEFAULT 0, -- Was this the customer's preferred food?
    points_earned INT DEFAULT 0,
    CONSTRAINT FK_Deliveries_GameSessions FOREIGN KEY (session_id) REFERENCES GameSessions(session_id),
    CONSTRAINT FK_Deliveries_FoodTypes FOREIGN KEY (food_id) REFERENCES FoodTypes(food_id)
);

-- Create GameSettings table for configuration values
CREATE TABLE GameSettings (
    setting_id INT IDENTITY(1,1) PRIMARY KEY,
    setting_name NVARCHAR(50) NOT NULL UNIQUE,
    setting_value NVARCHAR(100) NOT NULL,
    description NVARCHAR(200) NULL
);

-- Create Sounds table to track game sounds
CREATE TABLE Sounds (
    sound_id INT IDENTITY(1,1) PRIMARY KEY,
    sound_name NVARCHAR(50) NOT NULL UNIQUE,
    file_path NVARCHAR(200) NOT NULL,
    volume FLOAT DEFAULT 1.0,
    is_music BIT DEFAULT 0
);

-- Create Achievements table
CREATE TABLE Achievements (
    achievement_id INT IDENTITY(1,1) PRIMARY KEY,
    achievement_name NVARCHAR(50) NOT NULL UNIQUE,
    description NVARCHAR(200) NULL,
    points_value INT DEFAULT 0
);

-- Create PlayerAchievements junction table
CREATE TABLE PlayerAchievements (
    player_id INT NOT NULL,
    achievement_id INT NOT NULL,
    unlock_date DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (player_id, achievement_id),
    CONSTRAINT FK_PlayerAchievements_Players FOREIGN KEY (player_id) REFERENCES Players(player_id),
    CONSTRAINT FK_PlayerAchievements_Achievements FOREIGN KEY (achievement_id) REFERENCES Achievements(achievement_id)
);

-- Create LevelFoodTypes junction table to specify which foods appear in which levels
CREATE TABLE LevelFoodTypes (
    level_id INT NOT NULL,
    food_id INT NOT NULL,
    spawn_probability FLOAT DEFAULT 1.0, -- Higher means more likely
    PRIMARY KEY (level_id, food_id),
    CONSTRAINT FK_LevelFoodTypes_Levels FOREIGN KEY (level_id) REFERENCES GameLevels(level_id),
    CONSTRAINT FK_LevelFoodTypes_FoodTypes FOREIGN KEY (food_id) REFERENCES FoodTypes(food_id)
);

-- Create CustomerPreferences junction table
CREATE TABLE CustomerPreferences (
    customer_type_id INT NOT NULL,
    food_id INT NOT NULL,
    preference_weight FLOAT DEFAULT 1.0, -- Higher means stronger preference
    PRIMARY KEY (customer_type_id, food_id),
    CONSTRAINT FK_CustomerPreferences_CustomerTypes FOREIGN KEY (customer_type_id) REFERENCES CustomerTypes(customer_type_id),
    CONSTRAINT FK_CustomerPreferences_FoodTypes FOREIGN KEY (food_id) REFERENCES FoodTypes(food_id)
);

-- Create VisualEffects table for particles and effects
CREATE TABLE VisualEffects (
    effect_id INT IDENTITY(1,1) PRIMARY KEY,
    effect_name NVARCHAR(50) NOT NULL,
    default_size INT DEFAULT 5, -- From your code: size=5
    default_speed FLOAT DEFAULT 2.0, -- From your code: speed=2
    default_lifetime FLOAT DEFAULT 1.0, -- From your code: lifetime=1
    color_r INT DEFAULT 255,
    color_g INT DEFAULT 255,
    color_b INT DEFAULT 255,
    fade_rate FLOAT DEFAULT 255.0, -- From your code: self.fade_rate = 255 / lifetime
    description NVARCHAR(200) NULL
);

-- Create UI Elements table for buttons and UI components
CREATE TABLE UIElements (
    ui_element_id INT IDENTITY(1,1) PRIMARY KEY,
    element_type NVARCHAR(50) NOT NULL, -- 'button', 'text', etc.
    element_name NVARCHAR(50) NOT NULL,
    x_position INT NOT NULL,
    y_position INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    text_content NVARCHAR(100) NULL,
    color_r INT DEFAULT 255,
    color_g INT DEFAULT 255,
    color_b INT DEFAULT 255,
    hover_color_r INT DEFAULT 200,
    hover_color_g INT DEFAULT 200,
    hover_color_b INT DEFAULT 200,
    game_state INT NOT NULL, -- 0=MENU, 1=PLAYING, 2=GAME_OVER
    action_type NVARCHAR(50) NULL -- 'start_game', 'exit', 'restart', etc.
);

-- Create CustomerSpawnLocations table
CREATE TABLE CustomerSpawnLocations (
    location_id INT IDENTITY(1,1) PRIMARY KEY,
    level_id INT NOT NULL,
    spawn_side INT NOT NULL, -- 0=top, 1=right, 2=bottom, 3=left (from your code)
    min_position INT NOT NULL,
    max_position INT NOT NULL,
    spawn_weight FLOAT DEFAULT 1.0, -- Higher = more likely
    CONSTRAINT FK_CustomerSpawnLocations_Levels FOREIGN KEY (level_id) REFERENCES GameLevels(level_id)
);

-- Create indexes for performance
CREATE INDEX IX_PlayerCharacters_PlayerID ON PlayerCharacters(player_id);
CREATE INDEX IX_GameSessions_PlayerID ON GameSessions(player_id);
CREATE INDEX IX_GameSessions_CharacterID ON GameSessions(character_id);
CREATE INDEX IX_GameSessions_LevelID ON GameSessions(level_id);
CREATE INDEX IX_Deliveries_SessionID ON Deliveries(session_id);
CREATE INDEX IX_PlayerAchievements_PlayerID ON PlayerAchievements(player_id);
CREATE INDEX IX_CustomerSpawnLocations_LevelID ON CustomerSpawnLocations(level_id);

-- Insert initial game data

-- Insert food types from the game code
INSERT INTO FoodTypes (food_name, display_name, speed, lifespan)
VALUES
    ('pizza', 'Tropical Pizza Slice', 300, 2.0),
    ('smoothie', 'Ska Smoothie', 300, 2.0),
    ('icecream', 'Island Ice Cream Jam', 300, 2.0),
    ('pudding', 'Rasta Rice Pudding', 300, 2.0);

-- Insert initial game level
INSERT INTO GameLevels (level_name, customer_spawn_rate, missed_deliveries_limit, description)
VALUES ('Kitchen Chaos', 5.0, 10, 'Level 1 - Serve customers in a chaotic kitchen setting');

-- Insert default customer type
INSERT INTO CustomerTypes (type_name, min_patience, max_patience)
VALUES ('Regular', 10.0, 20.0);

-- Insert game settings
INSERT INTO GameSettings (setting_name, setting_value, description)
VALUES
    ('FPS', '60', 'Frames per second'),
    ('SCREEN_WIDTH', '768', 'Screen width in pixels'),
    ('SCREEN_HEIGHT', '768', 'Screen height in pixels');

-- Insert sounds from the game code
INSERT INTO Sounds (sound_name, file_path, volume, is_music)
VALUES
    ('pickup_sound', 'assets/sounds/characters/food_throw.wav', 1.0, 0),
    ('engine_sound', 'assets/sounds/vehicles/engine_idle.wav', 1.0, 0),
    ('button_sound', 'assets/sounds/ui/button_click.wav', 1.0, 0),
    ('background_music', 'assets/sounds/characters/food_throw.wav', 0.5, 1);

-- Insert achievements
INSERT INTO Achievements (achievement_name, description, points_value)
VALUES
    ('First Delivery', 'Make your first food delivery', 100),
    ('Speed Demon', 'Complete a level in under 60 seconds', 500),
    ('Food Maestro', 'Make 50 perfect deliveries', 1000),
    ('No Customer Left Behind', 'Complete a level with no missed customers', 2000);

GO