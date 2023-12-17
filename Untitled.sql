CREATE TABLE `fridge` (
  `fridge_id` integer PRIMARY KEY,
  `fridge_name` varchar(255),
  `fridge_content` integer
);

CREATE TABLE `fridge_content` (
  `content_id` integer PRIMARY KEY,
  `item_id` integer
);

CREATE TABLE `ingredients` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `amount` float,
  `unit` varchar(255)
);

CREATE TABLE `items` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `amount` float,
  `unit` varchar(255),
  `main_category` int,
  `sub_category` int
);

CREATE TABLE `main_category` (
  `id` integer PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `sub_category` (
  `id` integer PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `recipe` (
  `id` integer PRIMARY KEY,
  `title` varchar(255),
  `recipe_image` varchar(255),
  `instructions` integer,
  `used_ingredients` integer
);

CREATE TABLE `recipe_suggestion` (
  `id` integer PRIMARY KEY,
  `title` varchar(255),
  `recipe_image` varchar(255),
  `instructions` integer,
  `used_available` integer,
  `missed` integer
);

CREATE TABLE `used_available` (
  `id` integer PRIMARY KEY,
  `ingredients` integer
);

CREATE TABLE `missed` (
  `id` integer PRIMARY KEY,
  `ingredients` integer
);

CREATE TABLE `analyzed_instructions` (
  `id` integer PRIMARY KEY,
  `steps` integer,
  `instructions` varchar(255)
);

CREATE TABLE `used_ingredients` (
  `id` integer PRIMARY KEY,
  `ingredients` integer
);

ALTER TABLE `used_available` ADD FOREIGN KEY (`id`) REFERENCES `recipe_suggestion` (`used_available`);

ALTER TABLE `missed` ADD FOREIGN KEY (`id`) REFERENCES `recipe_suggestion` (`missed`);

ALTER TABLE `analyzed_instructions` ADD FOREIGN KEY (`id`) REFERENCES `recipe` (`instructions`);

ALTER TABLE `ingredients` ADD FOREIGN KEY (`id`) REFERENCES `used_ingredients` (`ingredients`);

ALTER TABLE `ingredients` ADD FOREIGN KEY (`id`) REFERENCES `used_available` (`ingredients`);

ALTER TABLE `ingredients` ADD FOREIGN KEY (`id`) REFERENCES `missed` (`ingredients`);

ALTER TABLE `recipe` ADD FOREIGN KEY (`used_ingredients`) REFERENCES `used_ingredients` (`id`);

ALTER TABLE `items` ADD FOREIGN KEY (`main_category`) REFERENCES `main_category` (`id`);

ALTER TABLE `items` ADD FOREIGN KEY (`sub_category`) REFERENCES `sub_category` (`id`);

ALTER TABLE `items` ADD FOREIGN KEY (`id`) REFERENCES `fridge_content` (`item_id`);

ALTER TABLE `fridge_content` ADD FOREIGN KEY (`content_id`) REFERENCES `fridge` (`fridge_content`);
