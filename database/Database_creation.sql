SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE game;
DROP TABLE goal;
DROP TABLE goal_reached;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE game (
  id INT PRIMARY KEY AUTO_INCREMENT,
  player_name VARCHAR(40) NOT NULL,
  current_level INT NOT NULL,
  current_location VARCHAR(40) NOT NULL,
  FOREIGN KEY (current_location) REFERENCES airport(ident)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE leaderboard (
  id INT PRIMARY KEY AUTO_INCREMENT,
  player_name VARCHAR(40) NOT NULL,
  score REAL NOT NULL,
  level INT NOT NULL,
  flights_number REAL NOT NULL,
  game_id INT,
  FOREIGN KEY (game_id) REFERENCES game(id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;