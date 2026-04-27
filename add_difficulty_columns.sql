-- Add difficulty level columns to existing tables
USE game_project;

-- Add difficulty_level to GAME table
ALTER TABLE GAME ADD COLUMN difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium';

-- Add difficulty_level to LEADERBOARD table
ALTER TABLE LEADERBOARD ADD COLUMN difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium';
