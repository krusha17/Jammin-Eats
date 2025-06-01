-- =============================================
-- Jammin' Eats Game Data Schema
-- Version: 1.0
-- Description: Core gameplay data and progression
-- =============================================

USE JamminEats;
GO

-- Player Progression Table
CREATE TABLE PlayerProgression (
    progression_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    current_money DECIMAL(10,2) DEFAULT 0.00,
    lifetime_earnings DECIMAL(10,2) DEFAULT 0.00,
    current_map INT DEFAULT 1,
    current_frame INT DEFAULT 1,
    tutorial_completed BIT DEFAULT 0,
    last_played DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_PlayerProgression_Players FOREIGN KEY (player_id) REFERENCES Players(player_id)
);

-- Food Economics Table (Prices vary by location)
CREATE TABLE FoodEconomics (
    economics_id INT IDENTITY(1,1) PRIMARY KEY,
    food_id INT NOT NULL,
    map_id INT NOT NULL,
    buy_price DECIMAL(5,2) NOT NULL,
    sell_price DECIMAL(5,2) NOT NULL,
    unlock_cost DECIMAL(8,2) DEFAULT 0.00,  -- Cost to unlock this food
    is_unlocked BIT DEFAULT 0,
    special_event_multiplier DECIMAL(3,2) DEFAULT 1.00,  -- For festival pricing
    CONSTRAINT FK_FoodEconomics_Food FOREIGN KEY (food_id) REFERENCES FoodTypes(food_id),
    CONSTRAINT FK_FoodEconomics_Maps FOREIGN KEY (map_id) REFERENCES GameLevels(level_id)
);

-- Player Inventory Table
CREATE TABLE PlayerInventory (
    inventory_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity INT DEFAULT 0,
    last_updated DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_PlayerInventory_Players FOREIGN KEY (player_id) REFERENCES Players(player_id),
    CONSTRAINT FK_PlayerInventory_Food FOREIGN KEY (food_id) REFERENCES FoodTypes(food_id)
);

-- Map Progression Table
CREATE TABLE MapProgression (
    map_progression_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    map_id INT NOT NULL,
    frame_number INT NOT NULL,
    is_completed BIT DEFAULT 0,
    best_score INT DEFAULT 0,
    best_earnings DECIMAL(8,2) DEFAULT 0.00,
    completion_date DATETIME,
    CONSTRAINT FK_MapProgression_Players FOREIGN KEY (player_id) REFERENCES Players(player_id),
    CONSTRAINT FK_MapProgression_Maps FOREIGN KEY (map_id) REFERENCES GameLevels(level_id)
);

-- Special Events Table
CREATE TABLE SpecialEvents (
    event_id INT IDENTITY(1,1) PRIMARY KEY,
    event_name NVARCHAR(100) NOT NULL,
    event_type NVARCHAR(50) NOT NULL,  -- 'cruise', 'flight', 'festival'
    map_id INT NOT NULL,
    profit_multiplier DECIMAL(3,2) DEFAULT 2.00,
    unlock_requirement_money DECIMAL(10,2),
    unlock_requirement_level INT,
    duration_days INT DEFAULT 1,
    CONSTRAINT FK_SpecialEvents_Maps FOREIGN KEY (map_id) REFERENCES GameLevels(level_id)
);

-- Transaction History (for analytics and debugging)
CREATE TABLE TransactionHistory (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    player_id INT NOT NULL,
    transaction_type NVARCHAR(50) NOT NULL,  -- 'purchase', 'sale', 'tip', 'penalty'
    amount DECIMAL(8,2) NOT NULL,
    item_description NVARCHAR(200),
    transaction_date DATETIME DEFAULT GETDATE(),
    map_id INT,
    frame_number INT,
    CONSTRAINT FK_TransactionHistory_Players FOREIGN KEY (player_id) REFERENCES Players(player_id)
);

-- Daily Challenges Table (future feature)
CREATE TABLE DailyChallenges (
    challenge_id INT IDENTITY(1,1) PRIMARY KEY,
    challenge_date DATE NOT NULL,
    challenge_type NVARCHAR(50) NOT NULL,
    target_value INT NOT NULL,
    reward_money DECIMAL(6,2) NOT NULL,
    description NVARCHAR(500)
);

-- Insert Initial Food Economics Data
INSERT INTO FoodEconomics (food_id, map_id, buy_price, sell_price, unlock_cost, is_unlocked)
VALUES
    -- Map 1 (Tutorial/Startup Beach)
    (1, 1, 3.00, 6.00, 0.00, 1),    -- Pizza (starter food)
    (2, 1, 4.00, 8.00, 20.00, 0),   -- Smoothie
    (3, 1, 5.00, 10.00, 50.00, 0),  -- Ice Cream
    (4, 1, 3.50, 7.00, 30.00, 0),   -- Pudding
    (5, 1, 6.00, 12.00, 100.00, 0); -- Rasgulla (premium)

-- Insert Special Events Data
INSERT INTO SpecialEvents (event_name, event_type, map_id, profit_multiplier, unlock_requirement_money)
VALUES
    ('Beach Reggae Festival', 'festival', 1, 2.5, 100.00),
    ('Caribbean Cruise', 'cruise', 2, 3.0, 500.00),
    ('Island Hop Flight', 'flight', 3, 2.0, 300.00),
    ('International Reggae Summit', 'festival', 4, 4.0, 1000.00),
    ('Bob Marley Birthday Bash', 'festival', 5, 5.0, 2000.00);

-- Create indexes for performance
CREATE INDEX IX_PlayerProgression_PlayerID ON PlayerProgression(player_id);
CREATE INDEX IX_PlayerInventory_PlayerID ON PlayerInventory(player_id);
CREATE INDEX IX_MapProgression_PlayerID ON MapProgression(player_id);
CREATE INDEX IX_TransactionHistory_PlayerID_Date ON TransactionHistory(player_id, transaction_date);