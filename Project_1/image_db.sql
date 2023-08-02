SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE=`TRADITIONAL,ALLOW_INVALID_DATES`;

DROP SCHEMA IF EXISTS `image_db` ;
CREATE SCHEMA IF NOT EXISTS `image_db` DEFAULT CHARACTER SET utf8 ;
USE `image_db` ;

DROP TABLE IF EXISTS `image_db`.`image` ;

CREATE TABLE IF NOT EXISTS `image_db`.`image` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(225) NOT NULL,
  `value` VARCHAR(225) NOT NULL,
  PRIMARY KEY (`id`)
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS `image_db`.`cache`;

CREATE TABLE IF NOT EXISTS `image_db`.`cache` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `no_items` INT NOT NULL DEFAULT 0,
  `total_size` BIGINT NOT NULL DEFAULT 0,
  `no_request` INT NOT NULL DEFAULT 0,
  `miss_rate` INT NOT NULL DEFAULT 0,
  `hit_rate` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS `image_db`.`cache_config`;

CREATE TABLE IF NOT EXISTS `image_db`.`cache_config` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `capacity` BIGINT NOT NULL DEFAULT 0,
  `policy` VARCHAR(225) NOT NULL,
  PRIMARY KEY (`id`)
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS `image_db`.`cache_image`;

CREATE TABLE IF NOT EXISTS `image_db`.`cache_image`(
    `cache_id` INT NOT NULL,
    `image_id` INT NOT NULL,
    primary key (`cache_id`,`image_id`),
    foreign key (cache_id) REFERENCES `image_db`.`cache`(id),
    foreign key (image_id) REFERENCES `image_db`.`image`(id)
)
ENGINE = InnoBD;
