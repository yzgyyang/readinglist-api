CREATE TABLE `readinglist`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(32) NULL,
  `password_hash` VARCHAR(128) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC));
  
CREATE TABLE `readinglist`.`lists` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL,
  `isprivate` TINYINT(1) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

CREATE TABLE `readinglist`.`books` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `isbn` VARCHAR(20) NULL,
  `title` VARCHAR(100) NULL,
  `author` VARCHAR(100) NULL,
  `category` VARCHAR(45) NULL,
  `coverurl` VARCHAR(45) NULL,
  `summary` VARCHAR(150) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `ISBN_UNIQUE` (`isbn` ASC));

CREATE TABLE `readinglist`.`relationships` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `list_id` INT NOT NULL,
  `book_id` INT NULL,
  PRIMARY KEY (`id`));
