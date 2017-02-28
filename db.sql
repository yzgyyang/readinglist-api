CREATE TABLE `readinglist`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(32) NULL,
  `password_hash` VARCHAR(128) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC));